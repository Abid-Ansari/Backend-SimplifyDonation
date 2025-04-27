from flask import Flask, jsonify
from flask_cors import CORS
from flask import render_template,redirect,request
from twilio.rest import Client
import random
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv



load_dotenv()

app = Flask(__name__)
CORS(app)

# setting up the database

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')=='True'  # Avoids a warning

db = SQLAlchemy(app)

class UsersOtp(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    phone=db.Column(db.String(10))
    otp=db.Column(db.String(6))


with app.app_context():  # Needed for DB operations
    db.create_all()  



@app.route('/', methods=['GET'])
def getmy():
    #return jsonify({"message": "Hello from Flask!"})
    return "hiiiiiii Abid"

@app.route('/api/data', methods=['GET'])
def get_data():
    #return jsonify({"message": "Hello from Flask!"})
    return jsonify({"message":"hii I am calling from flaskkkkkkkkkkk"})

@app.route('/form', methods=['GET'])
def get_form_data_and_send_confirmation():
    #return jsonify({"message": "Hello from Flask!"})
    
    phone_number_of_receiver = request.args.get('phone')
 
    print(phone_number_of_receiver)
    phone_number_of_receiver_str = '+91'+f'{phone_number_of_receiver}'
    print(phone_number_of_receiver_str)
    # Send a message
    account_sid = os.getenv('account_sid')
    auth_token = os.getenv('auth_token')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
       body="We have received your application.Thankyou so much for helping us make a difference.",  # Message content
       from_='+1 445 273 8357',  # Alphanumeric Sender ID
       to=phone_number_of_receiver_str)       # Recipient's phone number
    
    return redirect('http://localhost:3000/')


@app.route('/sendotp', methods=['GET','POST'])
def send_otp():
    
    phone_number_of_receiver = request.args.get('phone')
    print('phone_number_of_receiver',phone_number_of_receiver)
    phone_number_of_receiver_str = '+91'+f'{phone_number_of_receiver}'
    # Generate an OTP
    otp_length = 6
    otp=''
    for i in range(0,otp_length):
        otp += str(random.randint(1,9))

    to_add_in_otp_table = UsersOtp(phone=phone_number_of_receiver,otp=otp)
    db.session.add(to_add_in_otp_table)
    db.session.commit()

    account_sid = os.getenv('account_sid')
    auth_token = os.getenv('auth_token')
    body = f'Please enter this OTP to login into SimplifyWebApp {otp}'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
       body=body,  # Message content
       from_='+1 445 273 8357',  # Alphanumeric Sender ID
       to=phone_number_of_receiver_str)       # Recipient's phone number

    return redirect('http://localhost:3000/otpauthenticate')
                    
@app.route('/otpverify', methods=['GET','POST'])
def otp_verify():
    
    otp_from_receiver = request.get_json().get('otp')
    print(otp_from_receiver)
    last_otp_row = UsersOtp.query.order_by(UsersOtp.id.desc()).first()
    otp_sent = last_otp_row.otp
    print(otp_sent)
    if otp_from_receiver == otp_sent:
       db.session.delete(last_otp_row)
       return {'message':'success'}
    else:
       return {'message':'failure'}

if __name__ == '__main__':
    app.run(debug=True)
