from app.AWSConnections import AWSConnections

aws = AWSConnections()
awsSession = aws.getSession()

def saveUserDynamoDB (session, user):
    dynamodb = session.resource('dynamodb')
    table = table.put_item('Users')
    response = table.put_item(Item=user)
    return response

saveUserDynamoDB(awsSession,{"email":"local2@local.com", "juanito":12})