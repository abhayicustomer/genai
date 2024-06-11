from django.shortcuts import render
from .forms import PDFUploadForm
from django.http import JsonResponse
from .models import PDF
import os
import shutil
import index

# new
def upload_pdf(request):
    try:
        if request.method == 'POST':
            form = PDFUploadForm(request.POST, request.FILES)
            session_id = request.POST.get('session_id')

            # print(request.FILES)
            if form.is_valid():
                files = request.FILES.getlist('file')
                print("FILES--->", files)
                # if files:
                instances = PDF.objects.filter(session_id=session_id)
                if instances.exists():
                    directory_path = os.path.dirname(instances[0].file.path)
                    index_path = directory_path.replace(r'\data', '').replace(r'/data', '')
                    # print("DIRECTORY", directory_path)
                    print("INDEX DIRECTORY", index_path)
                    # Delete the directory and its contents
                    try:
                        # shutil.rmtree(directory_path)
                        shutil.rmtree(index_path)
                    except Exception as e:
                        print(e)

                    # Delete the model instances
                    instances.delete()

                for file in files:
                    pdf = PDF(file=file, session_id=session_id)
                    pdf.save()
                instances = PDF.objects.filter(session_id=session_id)
                directory_path = os.path.dirname(instances[0].file.path)
                index.create_index(directory_path)

                return JsonResponse({'result': 'File uploaded successfully!!!',
                                     "status": "PASS"})

            else:
                return JsonResponse({'result': 'Invalid data', "status": "FAIL"})
        else:
            return JsonResponse({'result': 'Wrong API request ', "status": "FAIL"})
    except Exception as e:
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})


def upload_csv(request):
    try:
        if request.method == 'POST':
            form = PDFUploadForm(request.POST, request.FILES)
            session_id = request.POST.get('session_id')

            # print(request.FILES)
            if form.is_valid():
                files = request.FILES.getlist('file')
                print("FILES--->", files)
                # if files:
                instances = PDF.objects.filter(session_id=session_id)
                if instances.exists():
                    directory_path = os.path.dirname(instances[0].file.path)
                    index_path = directory_path.replace(r'\data', '').replace(r'/data', '')
                    # print("DIRECTORY", directory_path)
                    print("INDEX DIRECTORY", index_path)
                    # Delete the directory and its contents
                    try:
                        # shutil.rmtree(directory_path)
                        shutil.rmtree(index_path)
                    except Exception as e:
                        print(e)

                    # Delete the model instances
                    instances.delete()

                for file in files:
                    pdf = PDF(file=file, session_id=session_id)
                    pdf.save()
                instances = PDF.objects.filter(session_id=session_id)
                directory_path = os.path.dirname(instances[0].file.path)
                

                return JsonResponse({'result': 'File uploaded successfully!!!',
                                     "status": "PASS"})

            else:
                return JsonResponse({'result': 'Invalid data', "status": "FAIL"})
        else:
            return JsonResponse({'result': 'Wrong API request ', "status": "FAIL"})
    except Exception as e:
        return JsonResponse({'result': 'Wrong API request ' + str(e), "status": "FAIL"})
