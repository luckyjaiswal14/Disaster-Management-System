"""
Volunteer routes for task assignment and status updates.
Handles Admin volunteer management and User volunteer actions.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Request, VolunteerAssignment, User
from datetime import datetime

volunteer_bp = Blueprint('volunteer', __name__)

def handle_error_response(msg, status_code):
    if request.is_json:
        return jsonify({'error': msg}), status_code
    flash(msg, 'danger')
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard for Admin (Management) and Volunteer (Actions)"""
    if current_user.is_admin:
        volunteers = User.query.filter_by(is_volunteer=True).all()
        assignments = VolunteerAssignment.query.order_by(VolunteerAssignment.assigned_at.desc()).all()
        
        # Filter out rejected or unassigned tasks
        active_assignments = [a for a in assignments if a.status != 'Rejected']
        assigned_req_ids = [a.request_id for a in active_assignments]
        
        unassigned_tasks = Request.query.filter(
            Request.status == 'Approved',
            ~Request.id.in_(assigned_req_ids if assigned_req_ids else [-1])
        ).all()
        
        return render_template('admin_volunteer_dashboard.html', 
                               unassigned_tasks=unassigned_tasks,
                               assignments=assignments,
                               volunteers=volunteers)
    else:
        if not current_user.is_volunteer:
            return render_template('volunteer_signup.html')
            
        assigned_request_ids = db.session.query(VolunteerAssignment.request_id).filter(VolunteerAssignment.status != 'Rejected').all()
        assigned_ids = [r[0] for r in assigned_request_ids]
        
        available_tasks = Request.query.filter(
            Request.status == 'Approved',
            ~Request.id.in_(assigned_ids if assigned_ids else [-1])
        ).all()
        
        my_assignments = VolunteerAssignment.query.filter_by(user_id=current_user.id).order_by(VolunteerAssignment.assigned_at.desc()).all()
        
        return render_template('volunteer_dashboard.html', 
                             available_tasks=available_tasks,
                             my_assignments=my_assignments)

@volunteer_bp.route('/signup', methods=['POST'])
@login_required
def signup():
    current_user.is_volunteer = True
    db.session.commit()
    flash('Welcome to the volunteer team!', 'success')
    return redirect(url_for('volunteer.dashboard'))

# ----------------- ADMIN ACTIONS -----------------

@volunteer_bp.route('/admin/assign', methods=['POST'])
@login_required
def admin_assign_task():
    if not current_user.is_admin:
        return handle_error_response('Admin access required', 403)
        
    request_id = request.form.get('request_id')
    volunteer_id = request.form.get('volunteer_id')
    
    if not request_id or not volunteer_id:
        return handle_error_response('Task and Volunteer are required', 400)
        
    req_obj = Request.query.get(request_id)
    volunteer = User.query.get(volunteer_id)
    
    if not req_obj or req_obj.status != 'Approved':
        return handle_error_response('Invalid task or task not approved', 400)
        
    existing = VolunteerAssignment.query.filter(VolunteerAssignment.request_id == request_id, VolunteerAssignment.status != 'Rejected').first()
    if existing:
        return handle_error_response('Task is already assigned', 409)
        
    assignment = VolunteerAssignment(
        user_id=volunteer_id,
        request_id=request_id,
        status='Pending Acceptance'
    )
    db.session.add(assignment)
    db.session.commit()
    
    flash(f'Task successfully assigned to {volunteer.name}. Awaiting their acceptance.', 'success')
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/admin/reassign/<int:assignment_id>', methods=['POST'])
@login_required
def admin_reassign_task(assignment_id):
    if not current_user.is_admin:
        return handle_error_response('Admin access required', 403)
        
    volunteer_id = request.form.get('volunteer_id')
    assignment = VolunteerAssignment.query.get_or_404(assignment_id)
    
    if not volunteer_id:
        return handle_error_response('Volunteer is required', 400)
        
    volunteer = User.query.get(volunteer_id)
    assignment.user_id = volunteer.id
    assignment.status = 'Pending Acceptance'
    db.session.commit()
    
    flash(f'Task reassigned to {volunteer.name}.', 'success')
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/admin/unassign/<int:assignment_id>', methods=['POST'])
@login_required
def admin_unassign_task(assignment_id):
    if not current_user.is_admin:
        return handle_error_response('Admin access required', 403)
        
    assignment = VolunteerAssignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    
    flash('Task unassigned successfully.', 'success')
    return redirect(url_for('volunteer.dashboard'))

# ----------------- VOLUNTEER ACTIONS -----------------

@volunteer_bp.route('/tasks/<int:request_id>/accept_available', methods=['POST'])
@login_required
def accept_available_task(request_id):
    """Volunteer accepts a task from the available list"""
    if not current_user.is_volunteer:
        return handle_error_response('Must be a volunteer', 403)
        
    req_obj = Request.query.get_or_404(request_id)
    if req_obj.status != 'Approved':
        return handle_error_response('Task not available', 400)
        
    existing = VolunteerAssignment.query.filter(VolunteerAssignment.request_id == request_id, VolunteerAssignment.status != 'Rejected').first()
    if existing:
        return handle_error_response('Task already assigned', 409)
        
    assignment = VolunteerAssignment(
        user_id=current_user.id,
        request_id=request_id,
        status='In Progress'
    )
    db.session.add(assignment)
    db.session.commit()
    
    flash('Task accepted! It is now In Progress.', 'success')
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/assignments/<int:assignment_id>/update', methods=['POST'])
@login_required
def update_assignment_status(assignment_id):
    """Volunteer updates their assigned task status (Accept, Reject, In Progress, Completed, Not Completed)"""
    assignment = VolunteerAssignment.query.get_or_404(assignment_id)
    
    if assignment.user_id != current_user.id:
        return handle_error_response('Unauthorized', 403)
        
    action = request.form.get('action')
    
    if action == 'Accept':
        assignment.status = 'In Progress'
        flash('You have accepted the assigned task.', 'success')
    elif action == 'Reject':
        assignment.status = 'Rejected'
        flash('You have rejected the assigned task.', 'warning')
    elif action == 'Completed':
        assignment.status = 'Completed'
        assignment.completed_at = datetime.utcnow()
        assignment.request_obj.status = 'Fulfilled'
        flash('Task marked as Completed!', 'success')
    elif action == 'Not Completed':
        assignment.status = 'Not Completed'
        flash('Task marked as Not Completed.', 'warning')
    elif action == 'In Progress':
        assignment.status = 'In Progress'
        flash('Task moved back to In Progress.', 'info')
    else:
        return handle_error_response('Invalid action', 400)
        
    db.session.commit()
    return redirect(url_for('volunteer.dashboard'))
