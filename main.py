import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:cloudinary_public/cloudinary_public.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class VideoUploadApp extends StatefulWidget {
  @override
  _VideoUploadAppState createState() => _VideoUploadAppState();
}

class _VideoUploadAppState extends State<VideoUploadApp> {
  File? _videoFile;
  String? _videoUrl;

  Future<void> _uploadVideo(ImageSource source) async {
    final ImagePicker picker = ImagePicker();
    final XFile? pickedFile = await picker.pickVideo(source: source);
    setState(() {
      if (pickedFile != null) _videoFile = File(pickedFile.path);
    });

    if (pickedFile != null) {
      final url = Uri.parse('https://api.cloudinary.com/v1_1/dggwc2zze/upload');
      final request = http.MultipartRequest('POST', url)
        ..fields['upload_preset'] = 'vjr2zecn'
        ..files
            .add(await http.MultipartFile.fromPath('file', _videoFile!.path));
      final Response = await request.send();
      if (Response.statusCode == 200) {
        final responseData = await Response.stream.toBytes();
        final responseString = String.fromCharCodes(responseData);
        final jsonMap = jsonDecode(responseString);
        setState(() {
          final url = jsonMap['url'];
          _videoUrl = url;
        });
      }
    }
  }

  Future<void> _sendVideoUrlToBackend() async {
    if (_videoUrl != null) {
      var url = 'https://bp-ow6374e7c-isha-cs-projects.vercel.app';
      var response = await http.post(
        Uri.parse(url),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, String>{
          'video_url': _videoUrl ?? '',
        }),
      );

      if (response.statusCode == 200) {
        print('Video URL sent to the backend');
        print("Response: ${response.body}");
      } else {
        print('Failed to send video URL to the backend');
        print(response.statusCode);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Video Upload App'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            ElevatedButton(
              onPressed: () {
                _uploadVideo(ImageSource.camera);
              },
              child: Text('Capture Video from Camera'),
            ),
            ElevatedButton(
              onPressed: () {
                _uploadVideo(ImageSource.gallery);
              },
              child: Text('Select Video from Gallery'),
            ),
            SizedBox(height: 20),
            Text('Video URL: ${_videoUrl ?? "Not available"}'),
            ElevatedButton(
              onPressed: () {
                _sendVideoUrlToBackend();
              },
              child: Text('Send Video URL to Backend'),
            ),
          ],
        ),
      ),
    );
  }
}
