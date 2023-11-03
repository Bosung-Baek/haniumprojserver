import os
from flask import Flask, jsonify, request
from models import db, User, Task, TaskStatus, Image

app = Flask(__name__)

@app.route('/user/<int:id>', methods=['GET', 'POST', 'DELETE'])
def handle_user(id):
    user = User.query.get(id)
    
    if request.method == 'GET':
        if user:
            tasks = [{'id': task.id, 'text': task.text} for task in user.tasks]
            return jsonify({'id': id, 'name': user.name, 'tasks': tasks}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    elif request.method == 'POST':
        name = request.get_json().get('name')
        if name:
            new_user = User(id=id, name=name)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'id': id, 'name': name}), 201
        else:
            return jsonify({'error': 'No name provided'}), 400

    elif request.method == 'DELETE':
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'result': 'User deleted'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404

@app.route('/task/<int:id>', methods=['GET', 'POST', 'DELETE'])
def handle_task(id):
    task = Task.query.get(id)
    
    if request.method == 'GET':
        if task:
            status = [{'id': status.id, 'boolean': status.boolean} for status in task.status]
            images = [{'id': image.id} for image in task.images]
            return jsonify({'id': id, 'text': task.text, 'status': status, 'images': images}), 200
        else:
            return jsonify({'error': 'Task not found'}), 404
            
    elif request.method == 'POST':
        text = request.get_json().get('text')
        user_id = request.get_json().get('user_id')
        if text and user_id:
            new_task = Task(id=id, text=text, user_id=user_id)
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'id': id, 'text': text, 'user_id': user_id}), 201
        else:
            return jsonify({'error': 'No text or user_id provided'}), 400

    elif request.method == 'DELETE':
        if task:
            db.session.delete(task)
            db.session.commit()
            return jsonify({'result': 'Task deleted'}), 200
        else:
            return jsonify({'error': 'Task not found'}), 404

@app.route('/status/<int:id>', methods=['POST', 'DELETE'])
def handle_status(id):
    if request.method == 'POST':
        boolean = request.get_json().get('boolean')
        task_id = request.get_json().get('task_id')
        if boolean is not None and task_id:
            new_status = TaskStatus(id=id, boolean=boolean, task_id=task_id)
            db.session.add(new_status)
            db.session.commit()
            return jsonify({'id': id, 'boolean': boolean, 'task_id': task_id}), 201
        else:
            return jsonify({'error': 'No boolean or task_id provided'}), 400

    elif request.method == 'DELETE':
        status = TaskStatus.query.get(id)
        if status:
            db.session.delete(status)
            db.session.commit()
            return jsonify({'result': 'Status deleted'}), 200
        else:
            return jsonify({'error': 'Status not found'}), 404

@app.route('/image/<int:id>', methods=['POST', 'DELETE'])
def handle_image(id):
    if request.method == 'POST':
        bitmap = request.get_json().get('bitmap')
        task_id = request.get_json().get('task_id')
        if bitmap and task_id:
            new_image = Image(id=id, bitmap=bitmap, task_id=task_id)
            db.session.add(new_image)
            db.session.commit()
            return jsonify({'id': id, 'bitmap': 'Image uploaded', 'task_id': task_id}), 201
        else:
            return jsonify({'error': 'No bitmap or task_id provided'}), 400

    elif request.method == 'DELETE':
        image = Image.query.get(id)
        if image:
            db.session.delete(image)
            db.session.commit()
            return jsonify({'result': 'Image deleted'}), 200
        else:
            return jsonify({'error': 'Image not found'}), 404
        
@app.route('/user/<int:user_id>/info', methods=['GET'])
def user_info(user_id):
    user = User.query.get(user_id)
    if user:
        tasks = []
        for task in user.tasks:
            task_info = {
                'id': task.id,
                'text': task.text,
                'status': [{'id': status.id, 'boolean': status.boolean} for status in task.status],
                'images': [{'id': image.id} for image in task.images]
            }
            tasks.append(task_info)
        return jsonify({'id': user.id, 'name': user.name, 'admin': user.admin, 'tasks': tasks}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jqiowejrojzxcovnklqnweiorjqwoijroi'

db.init_app(app)
db.app = app
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
