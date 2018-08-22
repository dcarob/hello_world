from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect, HttpResponse

from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import UpdateView
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse_lazy , reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, FormView, View
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.conf import settings 
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import time
from .datos import *
from .forms import * 
from .models import *
import base64

Columnas = None
Sheet = None
Filename =None
grupo_selec=0


# Create your views here.
class register(CreateView): #Vista para el registro de usuario
	"""docstring for register"""
	model = User
	template_name= "pfapp/register.html"
	form_class = UserForm

	success_url=reverse_lazy('login')
	

def logout (request): #Vista para cerrar sesion
	request.session.flush()
	return redirect("/")

def userprofile(request):
	current_user= request.user
	return render(request,'pfapp/index.html')

def editprofile(request): #Vista para editar perfil de usuario 
	if request.method == "POST":
		form=EditForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			return redirect('/profile/')
	else:
		form=EditForm(instance=request.user)
		return render(request, 'pfapp/edit.html',{'form':form})

def change_password(request): #Vista para cambiar clave de usuario
	if request.method == "POST":
		form=PasswordChangeForm(data=request.POST, user=request.user)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request,form.user)
			return redirect('/profile/')
		else:
			return redirect('/edit/')
	else:
		form=PasswordChangeForm(user=request.user)
		return render(request, 'pfapp/changepassword.html',{'form':form})
class ProfileList(ListView): #Vista para ver los grupos creados
	template_name = 'group_list.html'
	def get_queryset(self):
		return Group.objects.filter(user_id=self.request.user)
	
class GroupGroupMemberCreate(CreateView): #Vista para el formulario del grupo
	model = Group
	fields = ['group']
	labels= {'grupo': 'Group Name' }
	success_url = reverse_lazy('photo')
	def get_context_data(self, **kwargs):
		data = super(GroupGroupMemberCreate, self).get_context_data(**kwargs)
		if self.request.POST:
			data['groupmembers'] = GroupMemberFormSet(self.request.POST, self.request.FILES)
		else:
			data['groupmembers'] = GroupMemberFormSet()
		return data
	def form_valid(self, form):
		context = self.get_context_data()      
		groupmembers = context['groupmembers']
		with transaction.atomic():
			form.instance.user = self.request.user
      		self.object = form.save()	
      		if groupmembers.is_valid():
      			groupmembers.instance = self.object
      			groupmembers.save()
		return super(GroupGroupMemberCreate, self).form_valid(form)


def codificacion(request): #Vista para obtener el vector con las caracteristicas de las personas
	from os import listdir
	from os.path import join
	import face_recognition
	from face_recognition import face_locations
	from face_recognition.cli import image_files_in_folder
	import os
	import numpy as np

	x=[]
	y=[]
	pk=[]
	for p in GroupMembers.objects.raw('SELECT * FROM pfapp_groupmembers WHERE  groupid_id=( SELECT MAX(groupid_id) FROM pfapp_groupmembers )'):
		dire1=os.path.join('/home/ubuntu/SmartAttendance/static/media/', str(p.foto1))
		dire2=os.path.join('/home/ubuntu/SmartAttendance/static/media/', str(p.foto2))
		x.append(dire1)
		y.append(dire2)
		pk.append(p.id)
	for i in range(0,len(x)):
		image = face_recognition.load_image_file(x[i])
		cod=face_recognition.face_encodings(image)
		cod=np.array(cod)
		print(type(cod))
		GroupMembers.objects.filter(id =pk[i]).update(cod1 =cod[0])
	for i in range(0,len(y)):
		image = face_recognition.load_image_file(y[i])
		cod=face_recognition.face_encodings(image)
		cod=np.array(cod)
		print(type(cod))
		GroupMembers.objects.filter(id =pk[i]).update(cod2 =cod[0])
		

	print("listo")
	return redirect('profile-list')
def GroupList(request, group_grupo): #Vista para ver los integrantes del grupo
	query_group=GroupMembers.objects.filter(groupid=group_grupo)
	print(group_grupo)
	global grupo_selec
	grupo_selec=group_grupo
	#editGroup.grupo_selec2=grupo_selec
	context={
	'query_group':query_group
	}
	return render(request,'pfapp/lista.html',context)

def pictureUpload(request): #Vista para la foto tomada desde camara
	import MySQLdb

	if request.method == "POST" and request.is_ajax():
		name = request.POST['name']
		print("tiponame")
		name=str(name).replace('data:image/png;base64,','')
		print(type(name))
		date=time.strftime("%H:%M:%S")
		fileroute="static/media/pfapp/images/newimage" + date + ".png" 
		with open(fileroute, "wb") as f:
			f.write(name.decode('base64'))

			f.close()
			print("guarda foto")
			bd= MySQLdb.connect("127.0.0.1","root", "123pf","PF")
			print("conexion base")
			cursor = bd.cursor()
			print("se hizo cursor")
			cursor.execute("INSERT into pfapp_uploadphoto (picture) values ('%s')" %fileroute)
           	#(pk,class_dir,x[p])
			bd.commit()

		return HttpResponse("name")
	else:
		status= "Bad" 
		return HttpResponse(status)
			
class GroupPhotoEntry(CreateView): #Vista para cargar foto de asistencia
 
	model = UploadPhoto
	template_name= "pfapp/uploadphoto_form.html"
	form_class = UploadPhotoForm
	success_url=reverse_lazy('attendance')

def attendanceGenerator(request): #Vista para generar asistencia
	from os import listdir
	import os
	from os.path import join
	import pickle
	from PIL import Image, ImageFont,  ImageDraw,ImageEnhance
	import face_recognition
	from face_recognition import face_locations
	from face_recognition.cli import image_files_in_folder
	import cv2 
	from resizeimage import resizeimage
	import numpy as np
	import MySQLdb
	from django.template import loader
	from  more_itertools import unique_everseen
	bd= MySQLdb.connect("127.0.0.1","root", "123pf","PF")
	cursor = bd.cursor()
	global grupo_selec

	cursor.execute("SELECT id,cod1, cod2 FROM pfapp_groupmembers WHERE groupid_id = '%s'" %grupo_selec)
	results = cursor.fetchall()
	A = np.array([])
	for i in results:
		A = np.append(A, i[1])
		A= np.append(A, i[2])
	A=','.join(map(str, A)) 
	A=A.replace(' ',',')
	A=A.replace(',,,',',')
	A=A.replace(',,',',')
	A=A.replace(',,',',')
	print("Tipo de A")
	A=eval(A)
	A = [np.array(element) for element in A]
	known_face_encodings=A
	james=np.array([])
	B = np.array([])
	C = np.array([])
	for n in GroupMembers.objects.raw('SELECT id, nombreint FROM pfapp_groupmembers WHERE groupid_id = %s', [grupo_selec]):
		name=n.nombreint
		identity=n.id
		list_string = str(name)
		list_string2=str(identity)
		name=np.array(list_string)
		identity=np.array(list_string2)
		B = np.append(B, name)
		B = np.append(B, name)
	B=','.join(map(str, B))
	B=B.split(',')
	known_face_names=B
	tol=0.6
	james=B
	print(james)
	for p in UploadPhoto.objects.raw('SELECT * FROM pfapp_uploadphoto WHERE  id=( SELECT MAX(id) FROM pfapp_uploadphoto )'):
		dire1=os.path.join('/home/ubuntu/SmartAttendance/static/media/', str(p.picture))
		unknown_image = face_recognition.load_image_file(dire1)
		image=Image.fromarray(unknown_image)
		enhancer_object = ImageEnhance.Contrast(image)
		enhancer_object = ImageEnhance.Color(image)
		out = enhancer_object.enhance(1.3)
		out.save('/home/ubuntu/SmartAttendance/static/media/imagenmejorada.jpg')
		unknown_image = face_recognition.load_image_file('/home/ubuntu/SmartAttendance/static/media/imagenmejorada.jpg')
		height = np.size(unknown_image, 0)
		width = np.size(unknown_image, 1)
		if (width<2000 and height<2000):
			unknown_image = cv2.resize(unknown_image, (2500, 2000)) 
		face_locations = face_recognition.face_locations(unknown_image, number_of_times_to_upsample=0, model="hog")
		face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
		pil_image = Image.fromarray(unknown_image)

		#  Create a Pillow ImageDraw Draw instance to draw with
		draw = ImageDraw.Draw(pil_image)
		name_list=[]
		ids_list=[]
		ids=0
		uf=0
		unknown_list=[]
		# Loop through each face found in the unknown image
		for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
		# See if the face is a match for the known face(s)
			matches = face_recognition.face_distance(known_face_encodings, face_encoding)
			name = "Unknown"
			ids_str="Unknown"
			if(min(matches)<=tol):
				mindispos = matches.tolist().index(min(matches))
				name = known_face_names[mindispos]
				name_list.append(name)
				ids=ids+1
				ids_str=str(ids)
				ids_list.append(ids)
			else:
				uf=uf+1
				unknown_list.append(name+str(uf))
				ids_str="U"+str(uf)
				
				
		 # Draw a box around the face using the Pillow module
			draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

		 # Draw a label with a name below the face
			text_width, text_height = draw.textsize(ids_str)
			draw.rectangle(((left- 10, bottom - 10 ), (right - 10, bottom - 10)), fill=(0, 0, 255), outline=(0, 0, 255))
			draw.text((left + 6, bottom - text_height - 10), ids_str,fill=(0, 150, 255), font=ImageFont.truetype('Pillow/Tests/fonts/FreeSansBold.ttf', 60))


		 # Remove the drawing library from memory as per the Pillow docs
		del draw
		global grupo_selec
		 #  Display the resulting image
		date=time.strftime("%H:%M:%S")
		fileroute="/home/ubuntu/SmartAttendance/static/media/resultimage" + date + ".png" 
		pil_image.save(fileroute)
		fileroute2="/media/resultimage"+date+".png"
		bd= MySQLdb.connect("127.0.0.1","root", "123pf","PF")
		cursor = bd.cursor()
		cursor.execute("INSERT into pfapp_resultpicture (result, idgroup_id) values ('%s','%s')" %  (fileroute ,grupo_selec))
       	#(pk,class_dir,x[p])
		bd.commit()
		print(name_list)
		missing=set(james)-set(name_list)
		missing=list(missing)
		print(ids_list)
		print(missing)
		context={'names':name_list, 'missing':missing, 'fileroute':fileroute2, 'ids':ids_list, 'unknowns':unknown_list}
	    
	return render(request, 'pfapp/result.html', context)
	
	
def loadExcel(request):

	if request.method == 'POST':
		form = ExcelUpload(request.POST, request.FILES)
		if form.is_valid():
			#Get File from the form
			ExcelFile=request.FILES['ExcelFile']
			#Validating File
			if ExcelFile.name.find(".xls")==-1:
				print("NO EXCEL FILE")
				messages.add_message(request, messages.ERROR,"Choose a file (.xls o .xlsx)")
				return redirect("/loadexcel")
			#Saving the excel file
			rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
			fs=FileSystemStorage(location=rootpath)
			#delete de file if exist
			fs.delete(ExcelFile.name)
			filename=fs.save(ExcelFile.name,ExcelFile)
			sheetnames=Sheets(ExcelFile.name)
			#Saving Sessions
			request.session['sheetnames']=sheetnames
			request.session['ExcelName']=ExcelFile.name
			request.session['Uploaded']=True
			#request.session['user']='UsuarioPruebas'
			
			return redirect("/chooseSheet")
	else:
		form = ExcelUpload()
		#Deleting a file that will not be used
	try:
		if request.session['Uploaded']:
				rootpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Excel')
				fs=FileSystemStorage(location=rootpath)
				fs.delete(request.session['ExcelName'])
	except:
		print('Not File')
	request.session['Uploaded']=False
	return render(request,'pfapp/excelform.html',{'form':form})
	
def chooseSheet(request):
	if request.method=='POST':
		form=SheetSelection(request.POST, sheetlist=request.session['sheetnames'])
		if form.is_valid():
			#getting data from the form and Saving sessions to use it later
			sheet=form.cleaned_data['sheets']
			request.session['sheet']=sheet
			
			return redirect("/pickColumns")
	else:
		form=SheetSelection(sheetlist=request.session['sheetnames'])
	return render(request,'pfapp/sheet_form.html',{'form':form})

def pickcolumns(request):

	columnslist,ExcelFile=Columns(request.session['ExcelName'],request.session['sheet'])
	form=ColumnsSelection(columnslist=columnslist)
	global Filename 
	Filename= request.session['ExcelName']
	global Sheet
	Sheet=request.session['sheet']
	#Replacing NaN for ""
	ExcelFile=ExcelFile.replace(pd.np.nan,'', regex=True)
	#print nombre column
	#print(ExcelFile['Nombre'].tolist()[0])

	#Showing all rows Excel file
	ExcelHTML=ExcelFile.to_html(classes='table-striped " id = "my_table',index=False)
	if request.method=='POST':
		form=ColumnsSelection(request.POST  ,columnslist=columnslist)
		#get selection
		if form.is_valid():
			columns=form.cleaned_data['columns']
			request.session['columns']=columns
			global Columnas
			Columnas=request.session['columns']
			return redirect('/formset_excel')
		else:
			#Looking for error messages 
			if form.errors.as_data():
				for e in form.errors['columns'].as_data():
					e=str(e)
					e=e[2:len(e)-2]
					messages.add_message(request, messages.ERROR,e)
	return render(request,'pfapp/pickcolumns.html',{'form':form,'ExcelFile':ExcelFile})

class formset_excel(CreateView):

	model = Group
	fields = ['group']
	template_name= "pfapp/group_excel_form.html"
	success_url = reverse_lazy('photo')
	
	def get_context_data(self, **kwargs):

		#global variables
		global Filename
		global Sheet
		global Columnas
		#Vector con datos de nombres
		ExcelFile=FinalExcel(Filename,Sheet,Columnas)
		nombres=ExcelFile['Nombre'].values.tolist()
		correos=ExcelFile['Correo'].values.tolist()

		#create Formset
		GroupMemberExcelFormSet = inlineformset_factory(Group, GroupMembers,
                                            form=GroupMemberForm, extra=len(nombres))
		data = super(formset_excel, self).get_context_data(**kwargs)

		if self.request.POST:
			data['groupmembers'] = GroupMemberExcelFormSet(self.request.POST, self.request.FILES)
		else:
			data['groupmembers'] = GroupMemberExcelFormSet(initial=[{'nombreint': nombres[i] , 'correoint': correos[i]} for i in range(0,len(nombres))]) 
			
		return data
	def form_valid(self, form):
		context = self.get_context_data()      
		groupmembers = context['groupmembers']

		with transaction.atomic():

			#changing value
			form.instance.user = self.request.user
			self.object = form.save()	
			if groupmembers.is_valid():
				groupmembers.instance = self.object
				groupmembers.save()
		return super(formset_excel, self).form_valid(form)


def Testing(**kwargs):
		grupo_selec
		print(grupo_selec)
		retornar=grupo_selec
		print("fin")
		return grupo_selec
		
class editGroup(UpdateView): #Vista para el formulario de editar del grupo
 
	model = Group
	fields = ['group']
	labels= {'grupo': 'Group Name' }
	template_name= "pfapp/editgroup.html"
	success_url = reverse_lazy('editCod')
	def __init__(self):
		groupname = Group.objects.filter(id=grupo_selec)
		editGroup.initial={'group': groupname[0]}
	def get_object(self):
		return get_object_or_404(Group, pk=grupo_selec)
	def get_context_data(self, **kwargs):
		members = GroupMembers.objects.filter(groupid_id=grupo_selec)
		GroupMemberEditFormSet = inlineformset_factory(Group, GroupMembers, can_delete=True,
                                            form=GroupMemberEditForm, extra=len(members))
		data = super(editGroup, self).get_context_data(**kwargs)
		grupo=Group.objects.get(pk=grupo_selec)
		if self.request.POST:

			data['groupmembers'] = GroupMemberEditFormSet(self.request.POST, self.request.FILES)
		else:
			try:
				data['groupmembers'] = GroupMemberEditFormSet(initial=[{'nombreint': members[i].nombreint , 'correoint': members[i].correoint, 'foto1':members[i].foto1, 'foto2':members[i].foto2 } for i in range(0,len(members))])
			except (ObjectDoesNotExist, MultipleObjectsReturned):
				pass
		return data
	def form_valid(self, form):
		context = self.get_context_data()      
		groupmembers = context['groupmembers']
		with transaction.atomic():
			form.instance.user = self.request.user
			#self.object = form.save()
			if groupmembers.is_valid():
								
				#groupmembers.instance = self.object
					
				idgroup=Group.objects.only('id').get(id=grupo_selec)
				members = GroupMembers.objects.filter(groupid_id=grupo_selec)
				i=0
				#print(groupmembers.group)
				for f in groupmembers:
					nombreint = f.cleaned_data['nombreint']
					correoint= f.cleaned_data['correoint']
					foto1= f.cleaned_data['foto1'] 
					foto2= f.cleaned_data['foto2']
					try:	
						data=GroupMembers.objects.get(correoint=members[i].correoint)
						data.nombreint=nombreint
						data.correoint=correoint
						if foto1 != None:
							data.foto1=foto1
						if foto2 != None:
							data.foto2=foto2
						data.groupid=idgroup
						data.save()
						print("end try")
					except:
						print(nombreint)
						newmember=GroupMembers(groupid=idgroup, nombreint= nombreint, correoint=correoint,foto1=foto1, foto2=foto2)
						newmember.save()

					i=i+1
				dataGroup=Group.objects.get(id=grupo_selec)
				dataGroup.group=form.instance.group
				dataGroup.save()
				#groupmembers.save()
		return super(editGroup, self).form_valid(form)

def codificacionEdit(request): #Vista para obtener el vector con las caracteristicas de las personas
	from os import listdir
	from os.path import join
	import face_recognition
	from face_recognition import face_locations
	from face_recognition.cli import image_files_in_folder
	import os
	import numpy as np

	global grupo_selec
	x=[]
	y=[]
	pk=[]
	for p in GroupMembers.objects.raw('SELECT * FROM pfapp_groupmembers  WHERE groupid_id = %s', [grupo_selec]):
		dire1=os.path.join('/home/ubuntu/SmartAttendance/static/media/', str(p.foto1))
		dire2=os.path.join('/home/ubuntu/SmartAttendance/static/media/', str(p.foto2))
		x.append(dire1)
		y.append(dire2)
		pk.append(p.id)
	for i in range(0,len(x)):
		image = face_recognition.load_image_file(x[i])
		cod=face_recognition.face_encodings(image)
		cod=np.array(cod)
		print(type(cod))
		GroupMembers.objects.filter(id =pk[i]).update(cod1 =cod[0])
	for i in range(0,len(y)):
		image = face_recognition.load_image_file(y[i])
		cod=face_recognition.face_encodings(image)
		cod=np.array(cod)
		print(type(cod))
		GroupMembers.objects.filter(id =pk[i]).update(cod2 =cod[0])
		

	print("listo")
	return redirect('profile-list')


def Delete(request,part_id =None):
    deletemember = GroupMembers.objects.get(id=part_id)
    deletemember.delete()
    global grupo_selec
    return HttpResponseRedirect(reverse('detail', args=(grupo_selec,)))
