from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from config import Config
from extensions import db, login_manager
from models import User, ChatSession, ChatMessage
from services.medical_service import medical_processor
from services.chat_service import response_generator
from services.intent_service import detect_query_type, GreetingHandler

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create DB Tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('chat'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('chat'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    # Get active session or create new
    active_session = ChatSession.query.filter_by(user_id=current_user.id, is_active=True).order_by(ChatSession.created_at.desc()).first()
    if not active_session:
        active_session = ChatSession(user_id=current_user.id)
        db.session.add(active_session)
        db.session.commit()
    
    # Load messages
    messages = active_session.messages.order_by(ChatMessage.timestamp).all()
    
    # Get all conversations for sidebar
    all_conversations = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    
    return render_template('chat.html', messages=messages, session_id=active_session.id, conversations=all_conversations)

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    content = data.get('message')
    session_id = data.get('session_id')
    
    if not content or not session_id:
        return jsonify({'error': 'Missing data'}), 400
        
    chat_session = ChatSession.query.get(session_id)
    if not chat_session or chat_session.user_id != current_user.id:
        return jsonify({'error': 'Invalid session'}), 403

    # Save User Message
    user_msg = ChatMessage(session_id=session_id, sender='user', content=content)
    db.session.add(user_msg)
    db.session.commit()
    
    # Process Response
    response_text = process_query(content, chat_session)
    
    # Save Bot Message
    bot_msg = ChatMessage(session_id=session_id, sender='bot', content=response_text)
    db.session.add(bot_msg)
    db.session.commit()
    
    return jsonify({
        'content': response_text, 
        'sender': 'bot', 
        'timestamp': bot_msg.timestamp.strftime('%H:%M')
    })
    
@app.route('/api/clear_chat', methods=['POST'])
@login_required
def clear_chat():
    # Deactivate current session and start new
    data = request.json
    session_id = data.get('session_id')
    chat_session = ChatSession.query.get(session_id)
    if chat_session and chat_session.user_id == current_user.id:
        chat_session.is_active = False
        db.session.commit()
        
    # Create new
    new_session = ChatSession(user_id=current_user.id)
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({'status': 'cleared', 'new_session_id': new_session.id})

def process_query(query, chat_session):
    # Retrieve last disease from flask session or analyze chat history
    # For now, simplistic state in session
    last_disease = session.get(f'last_disease_{chat_session.id}')
    
    # Handle greetings
    if GreetingHandler.is_greeting(query):
        return GreetingHandler.get_greeting_response(query)
        
    query_type, intent = detect_query_type(query)
    
    if query_type == "unknown":
         return "⚠️ I'm RDguru++, specializing in rare diseases. Please ask about a disease, symptoms, or genetic condition."

    # Build memory context from recent messages
    recent_msgs = chat_session.messages.order_by(ChatMessage.timestamp.desc()).limit(5).all()[::-1]
    memory_context = "\n".join([f"{m.sender}: {m.content}" for m in recent_msgs])

    response = ""
    
    try:
        # 1. Identify Disease
        disease_match = medical_processor.find_best_disease_match(query)
        current_disease = disease_match if disease_match else last_disease
        
        if current_disease:
            session[f'last_disease_{chat_session.id}'] = current_disease
            db_context = medical_processor.get_db_info_for_disease(current_disease)
        else:
            db_context = ""

        # 2. Route based on intent
        if intent == "genetic":
            response = response_generator.generate_genetic_response(current_disease or query, db_context)
        elif intent == "mechanism":
            response = response_generator.generate_mechanism_response(current_disease or query, db_context)
        elif intent == "inheritance":
            response = response_generator.generate_inheritance_response(current_disease or query, db_context)
        elif intent == "tests":
            response = response_generator.generate_tests_response(current_disease or query, db_context)
        elif intent == "diagnosis" or intent == "info":
            # If explicit diagnosis with symptoms
            hpos = medical_processor.extract_hpo_terms(query)
            if hpos:
                preds = medical_processor.predict_ddqn(hpos)
                top_disease = preds[0] if preds else None
                # Update current disease if predicted
                if top_disease:
                    current_disease = top_disease
                    session[f'last_disease_{chat_session.id}'] = current_disease
                    db_context = medical_processor.get_db_info_for_disease(current_disease)

                response = response_generator.generate_diagnosis_response(
                    query, 
                    f"Predicted candidates: {', '.join(preds)}.\nTop match: {top_disease}", 
                    memory_context
                )
            else:
                 # General info about a named disease
                 if current_disease:
                      response = response_generator.generate_rag_response(query, db_context, current_disease, memory_context) # Need to add this method or use diagnosis
                 else:
                      response = response_generator.generate_followup_response(query, memory_context, current_disease)

        else:
            response = response_generator.generate_followup_response(query, memory_context, current_disease)
            
    except Exception as e:
        print(f"Error: {e}")
        response = "I encountered an error processing your medical query. Please try again."

    return response

@app.route('/api/get_conversations', methods=['GET'])
@login_required
def get_conversations():
    conversations = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    return jsonify([{
        'id': conv.id,
        'conversation_id': conv.conversation_id,
        'title': conv.title,
        'created_at': conv.created_at.strftime('%Y-%m-%d %H:%M')
    } for conv in conversations])

@app.route('/api/load_conversation/<int:session_id>', methods=['GET'])
@login_required
def load_conversation(session_id):
    chat_session = ChatSession.query.get(session_id)
    if not chat_session or chat_session.user_id != current_user.id:
        return jsonify({'error': 'Invalid session'}), 403
    
    messages = chat_session.messages.order_by(ChatMessage.timestamp).all()
    return jsonify({
        'session_id': chat_session.id,
        'conversation_id': chat_session.conversation_id,
        'title': chat_session.title,
        'messages': [{
            'sender': msg.sender,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M')
        } for msg in messages]
    })

@app.route('/api/delete_conversation/<int:session_id>', methods=['DELETE'])
@login_required
def delete_conversation(session_id):
    chat_session = ChatSession.query.get(session_id)
    if not chat_session or chat_session.user_id != current_user.id:
        return jsonify({'error': 'Invalid session'}), 403
    
    db.session.delete(chat_session)
    db.session.commit()
    
    return jsonify({'status': 'deleted'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
