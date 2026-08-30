"""
Administrative routes for request management and system oversight.
Requires admin privileges and handles critical resource allocation.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import User, Event, Resource, Donation, Request, AdminResponse, VolunteerAssignment

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    """Decorator to ensure user has admin privileges"""
    from functools import wraps
    
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview and pending requests"""
    pending_requests = Request.query.filter_by(status='Pending').order_by(Request.created_at.desc()).all()
    resources = Resource.query.all()
    events = Event.query.all()
    recent_donations = Donation.query.order_by(Donation.donated_at.desc()).limit(10).all()
    all_requests = Request.query.order_by(Request.created_at.desc()).limit(10).all()
    
    # Statistics
    stats = {
        'total_users': User.query.count(),
        'total_events': len(events),
        'total_requests': Request.query.count(),
        'pending_requests': len(pending_requests),
        'total_donations': Donation.query.count(),
    }
    
    
    volunteers = User.query.filter_by(is_volunteer=True).all()
    assignments = VolunteerAssignment.query.order_by(VolunteerAssignment.assigned_at.desc()).all()
    
    # Get approved but unassigned requests
    assigned_req_ids = [a.request_id for a in assignments]
    unassigned_tasks = Request.query.filter(
        Request.status == 'Approved',
        ~Request.id.in_(assigned_req_ids if assigned_req_ids else [-1])
    ).all()
    
    return render_template('admin_dashboard.html',
                         pending_requests=pending_requests,
                         resources=resources,
                         events=events,
                         donations=recent_donations,
                         all_requests=all_requests,
                         stats=stats,
                         volunteers=volunteers,
                         assignments=assignments,
                         unassigned_tasks=unassigned_tasks)

@admin_bp.route('/requests')
@login_required
@admin_required
def get_requests():
    """API endpoint for all requests with filtering and pagination"""
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = Request.query
    
    if status:
        query = query.filter_by(status=status)
    
    requests = query.order_by(Request.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    requests_data = [{
        'id': req.id,
        'user_name': req.user.name,
        'resource_name': req.resource.name,
        'event_name': req.event.name,
        'quantity': req.quantity,
        'urgency': req.urgency,
        'status': req.status,
        'created_at': req.created_at.isoformat()
    } for req in requests.items]
    
    return jsonify({
        'requests': requests_data,
        'total': requests.total,
        'pages': requests.pages,
        'current_page': page
    })

def handle_error_response(msg, status_code):
    if request.is_json:
        return jsonify({'error': msg}), status_code
    flash(msg, 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/request/<int:request_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_request(request_id):
    """Approve request in Python (replacing MySQL stored procedure)"""
    try:
        data = request.get_json() if request.is_json else request.form
        comment = data.get('comment', '')
        
        db.session.begin_nested()
        
        # Get pending request
        req_obj = Request.query.filter_by(id=request_id, status='Pending').first()
        if not req_obj:
            db.session.rollback()
            return handle_error_response('Request not found or not pending', 404)
            
        resource = Resource.query.get(req_obj.resource_id)
        if resource.available_quantity < req_obj.quantity:
            db.session.rollback()
            return handle_error_response('Insufficient resource quantity', 400)
            
        # Deduct from available quantity
        resource.available_quantity -= req_obj.quantity
        
        # Update request status
        req_obj.status = 'Approved'
        
        # Create admin response
        admin_resp = AdminResponse, VolunteerAssignment(
            request_id=request_id,
            admin_id=current_user.id,
            action='Approved',
            comment=comment
        )
        db.session.add(admin_resp)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Request approved successfully'}), 200
            
        flash('Request approved successfully', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        return handle_error_response('Action failed', 500)

@admin_bp.route('/request/<int:request_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_request(request_id):
    """Reject request in Python (replacing MySQL stored procedure)"""
    try:
        data = request.get_json() if request.is_json else request.form
        comment = data.get('comment', '')
        
        db.session.begin_nested()
        
        req_obj = Request.query.filter_by(id=request_id, status='Pending').first()
        if not req_obj:
            db.session.rollback()
            return handle_error_response('Request not found or not pending', 404)
            
        # Update request status
        req_obj.status = 'Rejected'
        
        # Create admin response
        admin_resp = AdminResponse, VolunteerAssignment(
            request_id=request_id,
            admin_id=current_user.id,
            action='Rejected',
            comment=comment
        )
        db.session.add(admin_resp)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Request rejected successfully'}), 200
            
        flash('Request rejected successfully', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        return handle_error_response('Action failed', 500)

@admin_bp.route('/resource/add', methods=['POST'])
@login_required
@admin_required
def add_resource():
    """Add a new resource to inventory"""
    try:
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        category = data.get('category', '').strip()
        description = data.get('description', '').strip()
        unit = data.get('unit', 'units').strip()
        quantity = data.get('quantity', 0)
        
        if not name or not category:
            return handle_error_response('Name and category are required', 400)
            
        try:
            quantity = int(quantity)
            if quantity < 0:
                quantity = 0
        except ValueError:
            quantity = 0
            
        # Check if resource already exists
        existing = Resource.query.filter_by(name=name).first()
        if existing:
            return handle_error_response('Resource with this name already exists', 409)
            
        resource = Resource(
            name=name,
            category=category,
            description=description,
            unit=unit,
            total_quantity=quantity,
            available_quantity=quantity
        )
        db.session.add(resource)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Resource added successfully', 'id': resource.id}), 201
            
        flash(f'Resource "{name}" added successfully', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        return handle_error_response('Failed to add resource', 500)

@admin_bp.route('/resources')
@login_required
@admin_required
def get_resources():
    """API endpoint for resource management"""
    resources = Resource.query.all()
    resources_data = [{
        'id': resource.id,
        'name': resource.name,
        'category': resource.category,
        'total_quantity': resource.total_quantity,
        'available_quantity': resource.available_quantity,
        'unit': resource.unit
    } for resource in resources]
    
    return jsonify(resources_data)

@admin_bp.route('/stats')
@login_required
@admin_required
def get_stats():
    """System statistics for admin dashboard"""
    total_users = User.query.count()
    total_events = Event.query.count()
    total_requests = Request.query.count()
    pending_requests = Request.query.filter_by(status='Pending').count()
    total_donations = Donation.query.count()
    
    # Resource utilization
    resources = Resource.query.all()
    resource_utilization = []
    for resource in resources:
        if resource.total_quantity > 0:
            utilization = ((resource.total_quantity - resource.available_quantity) / resource.total_quantity) * 100
        else:
            utilization = 0
        resource_utilization.append({
            'name': resource.name,
            'utilization': round(utilization, 2)
        })
    
    return jsonify({
        'total_users': total_users,
        'total_events': total_events,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'total_donations': total_donations,
        'resource_utilization': resource_utilization
    })


@admin_bp.route('/assign_task', methods=['POST'])
@login_required
@admin_required
def assign_task():
    try:
        data = request.get_json() if request.is_json else request.form
        request_id = data.get('request_id')
        volunteer_id = data.get('volunteer_id')
        
        if not request_id or not volunteer_id:
            return handle_error_response('Task and Volunteer are required', 400)
            
        req_obj = Request.query.get(request_id)
        volunteer = User.query.get(volunteer_id)
        
        if not req_obj or req_obj.status != 'Approved':
            return handle_error_response('Invalid task or task not approved', 400)
            
        if not volunteer or not volunteer.is_volunteer:
            return handle_error_response('Invalid volunteer', 400)
            
        existing = VolunteerAssignment.query.filter_by(request_id=request_id).first()
        if existing:
            return handle_error_response('Task is already assigned', 409)
            
        assignment = VolunteerAssignment(
            user_id=volunteer_id,
            request_id=request_id,
            status='In Progress'
        )
        db.session.add(assignment)
        db.session.commit()
        
        flash(f'Task successfully assigned to {volunteer.name}', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        return handle_error_response('Failed to assign task', 500)
