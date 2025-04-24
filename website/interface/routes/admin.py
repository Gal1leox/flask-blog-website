import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_file,
    abort,
    jsonify,
)
from flask_login import current_user

from website import db, limiter
from website.config import Config
from website.domain.models import User, UserRole
from website.utils import token_required, admin_required, TABLES, get_table_records

admin_bp = Blueprint(
    'admin', __name__,
    url_prefix='/admin',
    template_folder='../templates/shared/admin',
)


def get_current_user():
    return User.query.get(current_user.id) if current_user.is_authenticated else None


def base_context(user, active_page=''):
    is_admin = bool(user and user.role == UserRole.ADMIN)
    return {
        'is_admin': is_admin,
        'avatar_url': user.avatar_url if user else '',
        'token': Config.SECRET_KEY if is_admin else '',
        'db_name': Config.DB_NAME,
        'active_page': active_page,
        'theme': user.theme.value if user else 'system',
    }


@admin_bp.route('/database/', methods=['GET'])
@token_required
@admin_required
@limiter.limit('20/hour')
def database():
    user = get_current_user()
    table = request.args.get('table', '')

    tabs = [
        {'name': name, 'link': url_for('admin.database', table=name)},
    for name in TABLES.keys()
    ]

    records = get_table_records(table)
    attributes = TABLES.get(table, {}).get('columns', [])

    context = base_context(user, active_page='Database')
    context.update({
        'tabs': tabs,
        'table': table,
        'attributes': attributes,
        'records': records,
    })

    return render_template('pages/shared/admin/database.html', **context)


@admin_bp.route('/database/<string:table>/<int:record_id>', methods=['DELETE'])
@token_required
@admin_required
@limiter.limit('30/hour')
def delete_record(table, record_id):
    if table in ['post_images', 'post_tags', 'saved_posts']:
        flash('Deletion not allowed for this table.', 'danger')
        return jsonify(success=False, error='Forbidden'), 403

    table_info = TABLES.get(table)
    if not table_info:
        flash(f"Table '{table}' not found.", 'danger')
        return '', 404

    Model = table_info['table']
    record = Model.query.get(record_id)
    if not record:
        flash(f"Record {record_id} not found in {table}.", 'danger')
        return '', 404

    if table == 'users' and record.role == UserRole.ADMIN:
        flash('Cannot delete an admin user.', 'danger')
        return redirect(url_for('home.home'))

    db.session.delete(record)
    db.session.commit()

    flash(f'Record {record_id} deleted from {table}.', 'success')
    return jsonify(success=True), 200


@admin_bp.route('/database/<string:table>/all', methods=['DELETE'])
@token_required
@admin_required
@limiter.limit('5/hour')
def delete_records(table):
    table_info = TABLES.get(table)
    if not table_info:
        flash(f"Table '{table}' not found.", 'danger')
        return '', 404

    Model = table_info['table']
    query = Model.query

    if table == 'users':
        query = query.filter(Model.role != UserRole.ADMIN)

    deleted = query.delete(synchronize_session=False)
    db.session.commit()

    flash(f'Deleted {deleted} records from {table}.', 'success')
    return jsonify(success=True, deleted=deleted), 200


@admin_bp.route('/database/download', methods=['GET'])
@token_required
@admin_required
@limiter.limit('10/hour')
def download_db():
    db_path = os.path.abspath(
        os.path.join(current_app.root_path, '..', 'instance', Config.DB_NAME)
    )

    if not os.path.exists(db_path):
        abort(404)

    return send_file(db_path, as_attachment=True, download_name=Config.DB_NAME)


@admin_bp.route('/database/restore', methods=['POST'])
@token_required
@admin_required
@limiter.limit('5/hour')
def restore_db():
    if 'db_file' not in request.files:
        flash('No file uploaded.', 'danger')
        return jsonify(success=False, error='No file'), 400

    file = request.files['db_file']
    if not file or not file.filename.endswith('.db'):
        flash('Invalid file. Must be .db', 'danger')
        return jsonify(success=False, error='Invalid file'), 400

    db_path = os.path.abspath(
        os.path.join(current_app.root_path, '..', 'instance', Config.DB_NAME)
    )

    try:
        file.save(db_path)
        flash('Database restored.', 'success')
        return jsonify(success=True), 200
    except Exception as e:
        flash(f'Restore failed: {e}', 'danger')
        return jsonify(success=False, error=str(e)), 500
