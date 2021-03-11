package helloworld;

import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.util.Iterator;

import javax.imageio.ImageIO;

import com.google.common.primitives.Bytes;
import com.google.protobuf.ByteString;
import com.google.protobuf.BytesValue;

import helloworld.GreeterGrpc.GreeterBlockingStub;
import helloworld.Transferimg.HelloReply;
import helloworld.Transferimg.HelloRequest;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusException;
import io.grpc.StatusRuntimeException;

//import helloworld.GreeterGrpc.GreeterBlockingStub;
//import helloworld.Transferimg.HelloReply;
//import helloworld.Transferimg.HelloRequest;
//import io.grpc.ManagedChannel;
//import io.grpc.ManagedChannelBuilder;


public class TransferImgClient {

	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
		BufferedImage bImage = ImageIO.read(new File("/home/dinhhuy/Downloads/jang2.jpg"));
		System.out.println("mark 0");
	      ByteArrayOutputStream bos = new ByteArrayOutputStream();
	      ImageIO.write(bImage, "jpg", bos );
	      byte [] data = bos.toByteArray();
		      
	      ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost",50051).usePlaintext().build();
			

			GreeterBlockingStub greetStub = GreeterGrpc.newBlockingStub(channel);
			ByteString bstring = ByteString.copyFrom(data);

			HelloRequest hellorequest = HelloRequest.newBuilder().setName("Hoang My Linh").addPhoto(bstring).build();

			HelloReply helloreply = null;
			while (true) {
				try {
					helloreply = greetStub.sayHello(hellorequest);
					System.out.println(helloreply.getMessage());
					break;
				} catch (StatusRuntimeException e) {
					System.out.println("miss call");
				}
			}
						

	}

}
