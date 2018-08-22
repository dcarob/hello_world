# -*- coding: utf-8 -*-

from django import forms
from django.forms.formsets import BaseFormSet
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm , UserChangeForm

from .models import Users, UploadPhoto
from .models import Group
from .models import GroupMembers



class UserForm(UserCreationForm):
	
	class Meta:
		model = User
		fields = [ 'username',
					'first_name',
					'last_name',
					'email',
				]
		labels={ 'username': 'Username',
					'first_name': 'First Name',
					'last_name': 'Last Name',
					'email': 'E-mail',
					'password': 'Password'
				}

class LoginForm(forms.Form):
    email = forms.EmailField(label='E-mail',
    widget=forms.TextInput(attrs={'class':'form-control','placeholder':'e-mail','style':'width:30%'}))
    password = forms.CharField(label='Password', max_length=32, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'*******','style':'width:30%'}))

class EditForm(UserChangeForm):
	class Meta:
		model = User
		fields = [ 'username',
					'first_name',
					'last_name',
					'email',
					'password'

				]
		labels={ 'username': 'Username',
					'first_name': 'First Name',
					'last_name': 'Last Name',
					'email': 'E-mail',
					'password': 'Password'
				}
	
class GroupMemberForm(forms.ModelForm):

	
	nombreint= forms.CharField(label='Full Name',max_length= 80, widget=forms.TextInput(attrs=
                                {'class':'form-control', 'style':'width:100%'}))
	correoint= forms.EmailField(label= 'E-mail', max_length= 100, widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'example@correo.com',
                                'style':'width:100%'}))
	
	foto1 = forms.ImageField(label='Add picture 1', required=True)
	foto2 = forms.ImageField(label='Add picture 2', required=True)
	class Meta:
		model = GroupMembers
		exclude = ('cod1', 'cod2')

GroupMemberFormSet = inlineformset_factory(Group, GroupMembers,
                                            form=GroupMemberForm, extra=1)

class UploadPhotoForm(forms.ModelForm):
    picture=forms.ImageField(label='Add Group Picture', widget=forms.FileInput(attrs=
                                {'capture':'camera', 'accept':'image/*'}))
    class Meta:
        model=UploadPhoto
        fields = '__all__'

class ExcelUpload(forms.Form):
	ExcelFile=forms.FileField()

class SheetSelection(forms.Form):
    #Method that pass arguments to the form.
    def __init__(self,*args,**kwargs):
        sheetlist = kwargs.pop('sheetlist')
        super(SheetSelection,self).__init__(*args,**kwargs)
        self.fields['sheets'].choices = sheetlist

    sheets=forms.ChoiceField(widget=forms.Select(attrs=
                                {'class':'dropdown-header',
                                'style':'width:30%'}))

class ColumnsSelection(forms.Form):
    def __init__(self,*args,**kwargs):
        columnslist = kwargs.pop('columnslist')
        super(ColumnsSelection,self).__init__(*args,**kwargs)
        self.fields['columns'].choices = columnslist

    columns=forms.MultipleChoiceField(error_messages={'required': 'Choose at least one column'},
                                        widget=forms.CheckboxSelectMultiple())

class GroupMemberEditForm(forms.ModelForm):

	
	nombreint= forms.CharField(label='Full Name',max_length= 80, widget=forms.TextInput(attrs=
                                {'class':'form-control', 'style':'width:100%'}))
	correoint= forms.EmailField(label= 'E-mail', max_length= 100, widget=forms.TextInput(attrs=
                                {'class':'form-control',
                                'placeholder':'example@correo.com',
                                'style':'width:100%'}))
	
	foto1 = forms.ImageField(label='Add picture 1', required=False)
	foto2 = forms.ImageField(label='Add picture 2', required=False)
	class Meta:
		model = GroupMembers
		exclude = ('cod1', 'cod2')