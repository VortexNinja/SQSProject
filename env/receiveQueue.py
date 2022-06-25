import json
import gzip
import localstack_client.session as boto3

QUEUE_NAME = "login_queue"

# Create SQS client

queue_url = 'http://localhost:4566/000000000000/login-queue'

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='login-queue')

max_queue_messages = 10
message_bodies = []

# Keep reading in and deleting messages from the queue until it is empty
while True:
    messages_to_delete = []

# Can only do 10 messages at a time so we make a nested loop 
    for message in queue.receive_messages(MaxNumberOfMessages=10):
        
        # Takes a json string and converts it into a python dictionary
        data = json.loads(message.body)
        
        # Hashes the personal identifiable information
        masked_ip = hash(data['ip'])
        masked_device_id = hash(data['device_id'])
        
        # Changes the key_name by popping the value to a new name
        data['ip'] = masked_ip
        data['masked_ip'] = data.pop('ip')
        data['device_id'] = masked_device_id
        data['masked_device_id'] = data.pop('device_id')
        
# Made a list of all the message bodies to write to a json files
        message_bodies.append(data)
        
# Made a list to keep track of all the messages to delete
        messages_to_delete.append({
            'Id': message.message_id,
            'ReceiptHandle': message.receipt_handle
        })
        print(data)
        message.delete()
        
# Made a break condition for when there are no more messages to delete (queue is empty)
    if len(messages_to_delete) == 0:
        break
    else:
    	delete_response = queue.delete_messages(Entries=messages_to_delete)

    	

# Converts python dictionary object to json strings and writes it to a json file
with open("qdata.json", "a") as write_file:
    json.dump(message_bodies, write_file, indent=4)
