from concurrent import futures
import time
import logging
import cv2
import sys
import grpc
from PIL import Image
import io
import argparse
import transferimg_pb2
import transferimg_pb2_grpc
import numpy
import mysql.connector
from mysql.connector import Error
sys.path.append("/home/dinhhuy/testPJ/insightface_prj/deploy")
# from insightface_prj.deploy.face_model import FaceModel
from face_model import FaceModel
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

parser = argparse.ArgumentParser(description='face model test')
# general
parser.add_argument('--image-size', default='112,112', help='')
parser.add_argument('--model', default='model,0000', help='path to load model.')
parser.add_argument('--gpu', default=-1, type=int, help='gpu id')
args = parser.parse_args()
print('args:', args)
vec = args.model.split(',')
print('vec: ', vec)
model_prefix = vec[0]
model_epoch = int(vec[1])
model = FaceModel(args.gpu, model_prefix, model_epoch)

# connect to database:
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='webtoeicai',
                                         user='root',
                                         password='')
    if connection.is_connected():

        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        # sql_select_Query = "select * from student_test"
        # cursor.execute(sql_select_Query)
        # myresult = cursor.fetchall()
        # for x in myresult:
        #     print(x[0])

except Error as e:
    print("Error while connecting to MySQL", e)

##hoangcode
# img = Image.open("/home/dinhhuy/testPJ/insightface_prj/deploy/linh1.jpg")
# opencvImage = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
# img = model.get_input(opencvImage)
#
# f1 = model.get_feature(img)
# vector = np.array([1,2,3,4,5],dtype=np.float16)
# f1 = f1.astype(np.float16)
# f1 = abs(f1)
# vector = np.asarray(f1[:3], dtype=np.float16).tostring()
# # print("Feature: ", f1[:5])
# student_name=1
# sql_select_Query = "INSERT INTO student_test (Fullname, Features) VALUES (%s, %s)"
# val = (student_name,vector)
# cursor.execute(sql_select_Query,val)
# connection.commit()
##end
class Greeter(transferimg_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        # Accept the processing part after the picture passed by go
        data_stream = request.photo
        student_name = request.name
        data = io.BytesIO(data_stream)
        img = Image.open(data)
        opencvImage = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
        img = model.get_input(opencvImage)
        f1 = model.get_feature(img)
        # print("Feature: ", f1[:5])
        # print("Feature: ",f1.tobytes())
        # print('type f1: ', type(f1))

        cursor.execute("select * from student_test")
        myresult = cursor.fetchall()
        sim = 0
        count_test = 0
        for x in myresult:
            if(x[0] == student_name):
                # print('x[1]', x[1])
                f2 = numpy.frombuffer(x[1],dtype=numpy.float32)
                print('f2', f2)
                sim = numpy.dot(f1, f2)
                count_test = 1
                break
        if (count_test == 0):
            # store student in database
            bytes_feature = f1.tostring()
            cursor.execute('insert into student_test values(%s,%s)', (student_name,bytes_feature))
            connection.commit()
            message = "I received your informations: %s and stored in database" % student_name
        elif(count_test == 1):
            if(sim > 0.5):
                message = "true"
            else:
                message = "false"
        # return transferimg_pb2.HelloReply(message='Hello, %s! from python' % student_name)
        return transferimg_pb2.HelloReply(message = message)




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    transferimg_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
