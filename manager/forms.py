from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import *
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm,UserChangeForm,PasswordChangeForm
from django.contrib.auth.forms import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib.auth.hashers import check_password
from django.core.validators import FileExtensionValidator,URLValidator
from installation.forms import SiteConstants
from django.contrib.auth import authenticate
import re
from urllib.parse import urlparse


class UserResetPassword(PasswordResetForm):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter email address'}),error_messages={'required':'Email address is required'})

    def clean_email(self):
        email=self.cleaned_data['email']
        if  not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address does not exist')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Invalid email address')
        return email


class UsersContactForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control  input-sm input-round','placeholder':'Full name','aria-label':'name'}),error_messages={'required':'Full name is required'})
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'aria-required':'true','class':'form-control  input-sm input-round','type':'tel','aria-label':'phone','placeholder':'Phone'},initial="KE"),error_messages={'required':'Phone number is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-required':'true','class':'form-control  input-sm input-round','placeholder':'Email address','aria-label':'email'}),error_messages={'required':'Email address is required'})
    subject=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control  input-sm input-round','placeholder':'subject ','aria-label':'subject'}),error_messages={'required':'Subject is required'})
    message=forms.CharField(widget=forms.Textarea(attrs={'rows':5,'aria-required':'true','class':'form-control  input-sm','placeholder':'Message','aria-label':'message'}),error_messages={'required':'Message is required','min_length':'enter atleast 6 characters long'})

    class Meta:
        model=ContactModel
        fields=['name','phone','email','subject','message',]


    def clean_name(self):
        name=self.cleaned_data['name']
        if len(name.split(" ")) > 1:
            first_name=name.split(" ")[0]
            last_name=name.split(" ")[1]
            if not str(first_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
            elif not str(last_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
        return name

class UsersReplyForm(forms.ModelForm):
    reply=forms.CharField(widget=forms.Textarea(attrs={'rows':5,'cols':30,'aria-required':'true','class':'form-control  input-sm w-100','placeholder':'Message','aria-label':'reply'}),error_messages={'required':'Feedback is required','min_length':'enter atleast 6 characters long'})

    class Meta:
        model=ContactModel
        fields=['reply',]





class UserLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control','placeholder':'Username ','aria-label':'username'}),error_messages={'required':'Username  is required'})
    password=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control login-password','placeholder':'Password','aria-label':'password'}),error_messages={'required':'Password is required'})

    class Meta:
        model=User
        fields=['username','password',]

    def clean_username(self):
        username=self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            return username
        else:
            raise forms.ValidationError('invalid username')






class UserPasswordChangeForm(UserCreationForm):
    oldpassword=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control input-rounded','placeholder':'Old password','aria-label':'oldpassword'}),error_messages={'required':'Old password is required','min_length':'enter atleast 6 characters long'})
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control input-rounded','placeholder':'New password Eg Example12','aria-label':'password1'}),error_messages={'required':'New password is required','min_length':'enter atleast 6 characters long'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control input-rounded','placeholder':'Confirm new password','aria-label':'password2'}),error_messages={'required':'Confirm new password is required'})

    class Meta:
        model=User
        fields=['password1','password2']
    
    def clean_oldpassword(self):
        oldpassword=self.cleaned_data['oldpassword']
        if not self.instance.check_password(oldpassword):
            raise forms.ValidationError('Wrong old password.')
        else:
           return oldpassword 


#profileForm
class CurrentExtUserProfileChangeForm(forms.ModelForm):
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'class':'form-control input-rounded','type':'tel','aria-label':'phone','placeholder':'Phone example +25479626...'}),error_messages={'required':'Phone number is required'})
    bio=forms.CharField(widget=forms.Textarea(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'email'}),required=False)
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['phone','profile_pic','bio','nominal_roll',]

    
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if phone != self.instance.phone:
            if ExtendedAuthUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('A user with this phone number already exists.')
            else:
                return phone
        else:
           return phone 

class users_registerForm(UserCreationForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class':'fname form-control input-rounded','placeholder':'First name','aria-label':'first_name'}),error_messages={'required':'First name is required'})
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class':'lname form-control input-rounded','placeholder':'Last name','aria-label':'last_name'}),error_messages={'required':'Last name is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'email_field form-control input-rounded','placeholder':'Email address','aria-label':'email'}),error_messages={'required':'Email address is required'})
    username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control text-capitalize username_field input-rounded','placeholder':'Username ','aria-label':'username','readonly':True}),error_messages={'required':'Username is required'})
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-rounded text-capitalize','placeholder':'Password Eg Example12','aria-label':'password1'}),error_messages={'required':'Password is required','min_length':'enter atleast 6 characters long'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-rounded  text-capitalize','placeholder':'Confirm password','aria-label':'password2'}),error_messages={'required':'Confirm password is required'})

    class Meta:
        model=User
        fields=['first_name','last_name','email','username','password1','password2']


    def clean_first_name(self):
        first_name=self.cleaned_data['first_name']
        if not str(first_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
        return first_name
    
    def clean_last_name(self):
        last_name=self.cleaned_data['last_name']
        if not str(last_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
        return last_name
           

    def clean_email(self):
        email=self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('invalid email address')
        return email
    
    def clean_username(self):
        username=self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this registration number already exists')
        return username

#profileForm
class CurrentLoggedInUserProfileChangeForm(ModelForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded'}),error_messages={'required':'First name is required'})
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded','aria-label':'last_name'}),error_messages={'required':'Last name is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control text-capitalize input-rounded','aria-label':'email'}),error_messages={'required':'Email address is required'})
    is_active=forms.BooleanField(widget=forms.CheckboxInput(attrs={'aria-label':'is_active','id':'checkbox1'}),required=False)
    class Meta:
        model=User
        fields=['first_name','last_name','email','is_active',]


    def clean_first_name(self):
        first_name=self.cleaned_data['first_name']
        if not str(first_name).isalpha():
                raise forms.ValidationError('only characters are allowed.')
        return first_name
    
    def clean_last_name(self):
        last_name=self.cleaned_data['last_name']
        if not str(last_name).isalpha():
                raise forms.ValidationError('only characters are allowed.')
        return last_name

    def clean_email(self):
        email=self.cleaned_data['email']
        if email != self.instance.email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('A user with this email already exists.')
            try:
                validate_email(email)
            except ValidationError as e:
                raise forms.ValidationError('Invalid email address.')
            return email
        else:
           return email

    def clean_username(self):
        username=self.cleaned_data['username']
        if username != self.instance.username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('A user with this username already exists')
            return username
        return username


class EProfileForm(forms.ModelForm):
    is_cleared=forms.BooleanField(widget=forms.CheckboxInput(attrs={'aria-label':'is_cleared','id':'checkbox1'}),required=False)
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'class':'form-control input-rounded','type':'tel','aria-label':'phone','placeholder':'Phone'}),error_messages={'required':'Phone number is required'})
    paid_fee=forms.CharField(widget=forms.NumberInput(attrs={'class':'form-control input-rounded text-capitalize','placeholder':'Paid Fee','aria-label':'paid_fee'}),initial=0,required=False)
    reg_no=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded reg_no text-capitalize','placeholder':'Reg No eg EC/10/18 ','aria-label':'reg_no'}),error_messages={'required':'Registration number is required'})
    academic_year=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded text-capitalize','placeholder':'Academic Year eg 18/19','aria-label':'academic_year'}),error_messages={'required':'Academic year is required'})
    school=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded  text-capitalize','placeholder':'School of ','aria-label':'school'}),error_messages={'required':'School name is required'})
    course_name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded  text-capitalize','placeholder':'Course Name eg Electrical & Electronics Engineering ','aria-label':'course_name'}),error_messages={'required':'Course name is required'})
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['phone','profile_pic','reg_no','school','course_name','paid_fee','academic_year',]

    def clean_reg_no(self):
        reg_no=self.cleaned_data['reg_no']
        if self.instance.reg_no:
            if reg_no != self.instance.reg_no:
                if ExtendedAuthUser.objects.filter(reg_no=reg_no).exists():
                    raise forms.ValidationError('A user with this registration number already exists.')
                else:
                    return reg_no
            else:
               return reg_no
        else:
            if ExtendedAuthUser.objects.filter(reg_no=reg_no).exists():
                raise forms.ValidationError('A user with this registration number already exists.')
            else:
                return reg_no
    
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if self.instance.phone:
            if phone != self.instance.phone:
                if phone !='':
                    if ExtendedAuthUser.objects.filter(phone=phone).exists():
                        raise forms.ValidationError('A user with this phone number already exists.')
                    else:
                        return phone
                else:
                    raise forms.ValidationError('Phone number is required')
            else:
               return phone
        else:
            if phone !='':
                if ExtendedAuthUser.objects.filter(phone=phone).exists():
                    raise forms.ValidationError('A user with this phone number already exists.')
                else:
                    return phone
            else:
                raise forms.ValidationError('Phone number is required')

class ProfilePicForm(forms.ModelForm):
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['profile_pic',]

class SiteForm(forms.ModelForm):
    site_name=forms.CharField(widget=forms.EmailInput(attrs={'aria-label':'site_name','class':'form-control input-rounded','placeholder':'Site name'}),error_messages={'required':'Site Name is required'})
    description=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'description','class':'form-control','placeholder':'Site Description'}),error_messages={'required':'Site Description is required'})
    theme_color=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'theme_color','class':'form-control gradient-colorpicker input-rounded','placeholder':'Site Theme Color eg #ff0000'}),required=False)
    key_words=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'key_words','class':'form-control input-rounded tags','placeholder':'Site Keywords'}),required=False)
    site_url=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'site_url','class':'form-control input-rounded','placeholder':'Site URL'}),error_messages={'required':'Site URL is required'})
    favicon=forms.ImageField(
                                widget=forms.FileInput(attrs={'aria-label':'favicon','class':'custom-file-input','id':'customFileInput','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','ico'],message="Invalid image extension",code="invalid_extension")]
                                )
   
    class Meta:
        model=SiteConstants
        fields=['site_name','theme_color','site_url','description','key_words','favicon',]
    
    def clean_theme_color(self):
        theme_color=self.cleaned_data['theme_color']
        match=re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$',theme_color)
        if not match:
            raise forms.ValidationError('Invalid color code given')
        else:
            return theme_color
            
    def clean_site_url(self):
        site_url=self.cleaned_data['site_url']
        if URLValidator(site_url):
            return site_url
        else:
            raise forms.ValidationError('Invalid url')

#AddressConfigForm
class AddressConfigForm(forms.ModelForm):
    site_email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'site_email','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Site Email Address'}),error_messages={'required':'Address is required'})
    site_email2=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'site_email2','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Site Additional Email Address'}),required=False)
    address=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'address','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Address is required'})
    location=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'location','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Location is required'})
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'aria-label':'phone','style':'text-transform:lowercase;','class':'form-control input-rounded'},initial='KE'),required=False)
    class Meta:
        model=SiteConstants
        fields=['address','location','phone','site_email','site_email2']
    
    def clean_site_email(self):
        email=self.cleaned_data['site_email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address.')
        return email
    
    def clean_site_email2(self):
        email=self.cleaned_data['site_email2']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address.')
        return email


#social form
class UserSocialForm(forms.ModelForm):
    facebook=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'facebook','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Facebook Link'}),required=False)    
    twitter=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'twitter','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Twitter Link'}),required=False)    
    github=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'github','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Github Link'}),required=False)  
    instagram=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'instagram','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Instagram Link'}),required=False)    
    linkedin=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'linkedin','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Linkedin Link'}),required=False)   
    youtube=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'youtube','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Youtube Link'}),required=False)    
    whatsapp=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'whatsapp','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Whats App'}),required=False)
    class Meta:
        model=SiteConstants
        fields=['facebook','twitter','linkedin','instagram','whatsapp','youtube','github',]

    def clean_facebook(self):
        facebook=self.cleaned_data['facebook']
        if URLValidator(facebook):
                output=urlparse(facebook)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [facebook,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_twitter(self):
        twitter=self.cleaned_data['twitter']
        if URLValidator(twitter):
                output=urlparse(twitter)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [twitter,username]
        else:
            raise forms.ValidationError('Invalid url')
    

    def clean_github(self):
        github=self.cleaned_data['github']
        if URLValidator(github):
                output=urlparse(github)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [github,username]
        else:
            raise forms.ValidationError('Invalid url')
    def clean_instagram(self):
        instagram=self.cleaned_data['instagram']
        if URLValidator(instagram):
                output=urlparse(instagram)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [instagram,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_linkedin(self):
        linkedin=self.cleaned_data['linkedin']
        if URLValidator(linkedin):
                output=urlparse(linkedin)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [linkedin,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_youtube(self):
        youtube=self.cleaned_data['youtube']
        if URLValidator(youtube):
                output=urlparse(youtube)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Channel id parameter missing')
                else:
                    return [youtube,username]
        else:
            raise forms.ValidationError('Invalid url')
    def clean_whatsapp(self):
        whatsapp=self.cleaned_data['whatsapp']
        if URLValidator(whatsapp):
            output=urlparse(whatsapp)
            username=output.path.strip('/')
            if not username:
                raise forms.ValidationError('username parameter missing')
            else:
                return [whatsapp,username]
        else:
            raise forms.ValidationError('Invalid url')

#WorkingConfigForm
class WorkingConfigForm(forms.ModelForm):
    working_days=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'working_days','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Working days is required'})
    working_hours=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'working_hours','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Working hours is required'})

    class Meta:
        model=SiteConstants
        fields=['working_days','working_hours',]

year=[
        ('Y5','Y5'),
        ('Y4','Y4'),
        ('Y3','Y3'),
        ('Y2','Y2'),
        ('Y1','Y1'),    
    ]

sem=[
        ('S1','S1'),
        ('S2','S2'),
    ]


class CourseForm(forms.ModelForm):
    fee=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded','placeholder':'Tution fee','aria-label':'fee'}),error_messages={'required':'Tution fee is required'})
    course_name=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded','placeholder':'Course name eg Electrical & Electronics Engineering','aria-label':'course_name'}),error_messages={'required':'Course name is required'})
    stamp=forms.ImageField(
                                widget=forms.FileInput(attrs={'aria-label':'stamp','class':'custom-file-input','id':'customFileInput1','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','ico'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=CourseModel
        fields=['course_name','school','stamp','fee',]

    def clean_course_name(self):
        course_name=self.cleaned_data['course_name']
        if self.instance.school:
            if course_name != self.instance.course_name:
                if CourseModel.objects.filter(course_name=course_name).exists():
                    raise forms.ValidationError('Course name already exists.')
                else:
                    return course_name
            else:
               return course_name
        else:
            if CourseModel.objects.filter(course_name=course_name).exists():
                raise forms.ValidationError('Course name already exists.')
            else:
                return course_name


class SchoolForm(forms.ModelForm):
    school=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded text-capitalize','placeholder':'School of ','aria-label':'school'}),error_messages={'required':'School name is required'})

    class Meta:
        model=SchoolModel
        fields=['school',]

    def clean_school(self):
        school=self.cleaned_data['school']
        if self.instance.school:
            if school != self.instance.school:
                if SchoolModel.objects.filter(school=school).exists():
                    raise forms.ValidationError('School name already exists.')
                return school
            else:
               return school
        else:
            if SchoolModel.objects.filter(school=school).exists():
                raise forms.ValidationError('School name already exists.')
            else:
                return school


class SemForm(forms.ModelForm):
    year=forms.ChoiceField(choices=year,initial="Y4", error_messages={'required':'Year of study is required','aria-label':'year'},
    widget=forms.Select(attrs={'class':'form-control input-rounded','placeholder':'Year of study'}))    
    sem=forms.ChoiceField(choices=sem,initial="S1", error_messages={'required':'Sem of study is required','aria-label':'sem'},
    widget=forms.Select(attrs={'class':'form-control input-rounded','placeholder':'Year of study'}))      
    academic_year=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded','placeholder':'Current Academic Year eg 20/21 ','aria-label':'academic_year'}),error_messages={'required':'Current academic year is required'})
    course_code=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded','placeholder':'Course code ','aria-label':'course_code'}),error_messages={'required':'Course code is required'})
    course_name=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded','placeholder':'Course ','aria-label':'course_name'}),error_messages={'required':'Course name is required'})
    course_title=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded','placeholder':'Course Title ','aria-label':'course_title'}),error_messages={'required':'Course Title is required'})
    school=forms.CharField(widget=forms.TextInput(attrs={'class':'text-upper form-control input-rounded','placeholder':'School of ','aria-label':'school'}),error_messages={'required':'School is required'})

    class Meta:
        model=SemModel
        fields=['year','sem','course_code','school','course_title','course_name','academic_year',]

    def clean_course_code(self):
        course_code=self.cleaned_data['course_code']
        if self.instance.course_code:
            if course_code != self.instance.course_code:
                if SemModel.objects.filter(course_code=course_code).exists():
                    raise forms.ValidationError('Course  code  already exists.')
                else:
                    return course_code
            else:
               return course_code
        else:
            if SemModel.objects.filter(course_code=course_code).exists():
                raise forms.ValidationError('Course  code  already exists.')
            else:
                return course_code


    def clean_course_title(self):
        course_title=self.cleaned_data['course_title']
        if self.instance.course_title:
            if course_title != self.instance.course_title:
                if SemModel.objects.filter(course_title=course_title).exists():
                    raise forms.ValidationError('course title  already exists.')
                else:
                    return course_title
            else:
               return course_title
        else:
            if SemModel.objects.filter(course_title=course_title).exists():
                raise forms.ValidationError('course title  already exists.')
            else:
                return course_title

class NominalRollForm(forms.ModelForm):
    nominal_roll=forms.BooleanField(widget=forms.CheckboxInput(attrs={'aria-label':'nominal_roll','id':'checkbox1'}),error_messages={'required':'You are required to sign nominal roll before completing course registration.'})
    
    class Meta:
        model=ExtendedAuthUser
        fields=['nominal_roll',]
