/*proloader*/
function load()
{
  document.querySelector('.placeholder').style.display="none";
  document.querySelector('.main-display').style.display="block";
}

/*insection observer API */
function observerImages()
{
    var images=document.querySelectorAll('[data-src]'),
    imgOpts={},
    observer=new IntersectionObserver((entries,observer)=>
    {
        entries.forEach((entry)=>
        {
            if(!entry.isIntersecting) return;
            const img=entry.target;
            const newUrl=img.getAttribute('data-src');
            img.src=newUrl;
            observer.unobserve(img);
        });
    },imgOpts);
  
    images.forEach((image)=>
    {
      observer.observe(image)
    });
}

$(document).ready(function()
{
  observerImages();
});

/*submit register form*/
$(document).on('submit','.ContactForm',function()
{
  var el=$(this),
  btn_text=el.find('button:last').text(),
  form_data=new FormData(this);
  el.find("input,textarea,select").attr('aria-invalid',false).parents('.form-group').removeClass('error').find('.help-block').html('');
  el.children().find('.is-invalid').removeClass('is-invalid');
  el.parents('.form-wrapper').find('.load-overlay .loader-container').html(`<div class="loader"><svg class="circular" viewBox="25 25 50 50"><circle class="path" cx="50" cy="50" r="10" fill="none" stroke-width="2" stroke-miterlimit="10"/></svg></div>`);
  $.ajax(
    {
      url:el.attr('action'),
      method:el.attr('method'),
      dataType:'json',
      data:form_data,
      contentType:false,
      cache:false,
      processData:false,
      beforeSend:function()
      {
        el.parents('.form-wrapper').find('.load-overlay').show();
        el.find('button:last').attr('disabled',true).html('<i class="spinner-border spinner-border-sm" role="status"></i> Please wait...');
        el.parents('.form-wrapper').find('.overlay-close').removeClass('btn-remove');
      },
      success:function(callback)
      {
        el.parents('.form-wrapper').find('.overlay-close').addClass('btn-remove');
        el.parents('.form-wrapper').find('.load-overlay').hide();
        el.find('button:last').attr('disabled',false).text(btn_text);
        if(callback.valid)
        {
            el[0].reset();
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Success');
            $('.small-model').find('.modal-body').html('<div class="text-success text-center"><i class="fa fa-check-circle"></i> '+callback.message+'</div>');
        }
        else
        {
            $.each(callback.form_errors,function(key,value)
            {
              el.find("input[aria-label='"+key+"'],select[aria-label='"+key+"']").attr('aria-invalid',true).parents('.form-group,.form-check').addClass('error').find('.help-block').html('<ul role="alert"><li>'+value+'</li></ul>');
            });
        }
      },
      error:function(err)
      {
        el.parents('.form-wrapper').find('.overlay-close').addClass('btn-remove');
        el.find('button:last').attr('disabled',false).text(btn_text);
        el.parents('.form-wrapper').find('.load-overlay .loader-container').html('<span class="text-danger font-weight-bold"> <i class="zmdi zmdi-alert-triangle"></i> '+err.status+' :'+err.statusText+'</span>.');
      }
    });
  return false;
});

$(document).on('click','.btn-remove',function()
{
  $(this).parent().find('.loader-container').html(`<div class="loader"><svg class="circular" viewBox="25 25 50 50"><circle class="path" cx="50" cy="50" r="10" fill="none" stroke-width="2" stroke-miterlimit="10"/></svg></div>`);
  $(this).parent().hide(); 
  return false;                                                
});

$(document).on('click','.reveal',function()
{
    var el=$(this);
    if($('.login-password').attr('type') =='password')
    {
        $('.login-password').attr('type','text');
        el.removeClass('fa-eye-slash').addClass('fa-eye');
    }
    else
    {
        $('.login-password').attr('type','password');
        el.removeClass('fa-eye').addClass('fa-eye-slash');
    }
});

$(document).on('submit','.loginForm',function()
{
  var el=$(this),
  btn_text=el.find('button').text(),
  urlparams=new URLSearchParams(window.location.search),
  next=urlparams.get('next'),
  form_data=new FormData(this);
  el.children().find('.is-invalid').removeClass('is-invalid');
  el.parents('.card').find('.load-overlay .loader-container').html(`<div class="loader"><svg class="circular" viewBox="25 25 50 50"><circle class="path" cx="50" cy="50" r="10" fill="none" stroke-width="2" stroke-miterlimit="10"/></svg></div>`);
  $.ajax(
  {
    url:el.attr('action'),
    method:el.attr('method'),
    dataType:'json',
    data:form_data,
    contentType:false,
    cache:false,
    processData:false,
    beforeSend:function()
    {
      $(document).find('.feedback').html('');
      el.find('button').html('<i class="spinner-border spinner-border-sm" role="status"></i> Please wait...').attr('disabled',true);
      el.parents('.card').find('.load-overlay').show();
      el.parents('.card').find('.overlay-close').removeClass('btn-remove');
    },
    success:function(callback)
    {
      el.find('button').html(btn_text).attr('disabled',false);
      el.parents('.card').find('.overlay-close').addClass('btn-remove');
      el.parents('.card').find('.load-overlay').hide();
      if(!callback.valid)
      {
        $.each(callback.form_errors,function(prefix,value)
        {
          el.find("input[name='"+prefix+"'],textarea[name='"+prefix+"'],select[name='"+prefix+"']").addClass('is-invalid').parents('.form-group').find('.feedback').addClass('invalid-feedback').html('<i class="fa fa-exclamation-circle"></i> '+value[0]);
        });
      }
      else
      {
        if(next)
        {
            window.location=next;
        }
        else
        {
            window.location='/dashboard';
        }
      }
    },
    error:function(err)
    {
      el.find('button').html(btn_text).attr('disabled',false);
      el.parents('.card').find('.load-overlay .loader-container').html('<span class="text-danger font-weight-bold"> <i class="fa fa-alert-triangle"></i> '+err.status+' :'+err.statusText+'</span>.');
    }
  });
  return false;
});


$(document).on('change','.profile',function()
{
    var el=$(this),
    file=el.get(0).files[0],
    ext=el.val().substring(el.val().lastIndexOf('.')+1).toLowerCase();
    if(file && (ext=='jpg' || ext=='png' || ext=='jpeg' || ext=='gif'))
    {
        var reader=new FileReader();
        reader.onload=function(e)
        {
          $('.imagecard').find('img').attr('src',reader.result);
          $('.uploader').show();
          $('.selector').hide();
        }
        reader.readAsDataURL(file);
    }
    else
    {
      $('.small-model').modal({show:true});
      $('.small-model').find('.modal-title').text('Warning');
      $('.small-model').find('.modal-body').html('<div class="text-warning text-center"><i class="fa fa-alert-triangle"></i> Invalid image format</div>');
    }
});

$(document).on('keyup','.fname',function()
{
  $('.ffname').text($(this).val());
});
$(document).on('keyup','.lname',function()
{
  $('.llname').text($(this).val());
});


$(document).on('submit','.ActiveForm',function()
{
  var el=$(this),
  btn_text=el.find('button:last').text(),
  form_data=new FormData(this);
  $('.feedback').html('');
  el.children().find('.is-invalid').removeClass('is-invalid');
  el.parents('.card , .editor').find('.load-overlay .loader-container').html(`<div class="loader"><svg class="circular" viewBox="25 25 50 50"><circle class="path" cx="50" cy="50" r="10" fill="none" stroke-width="2" stroke-miterlimit="10"/></svg></div>`);
  $.ajax(
    {
      url:el.attr('action'),
      method:el.attr('method'),
      dataType:'json',
      data:form_data,
      contentType:false,
      cache:false,
      processData:false,
      beforeSend:function()
      {
        el.parents('.card,.editor').find('.load-overlay').show();
        el.find('button:last').attr('disabled',true).html('<i class="spinner-border spinner-border-sm" role="status"></i> Please wait...');
        el.parents('.card , .editor').find('.overlay-close').removeClass('btn-remove');
      },
      success:function(callback)
      {
        el.parents('.card,.editor').find('.overlay-close').addClass('btn-remove');
        el.parents('.card,.editor').find('.load-overlay').hide();
        el.find('button:last').html(btn_text).attr('disabled',false);
        if(callback.valid)
        {
            el[0].reset();
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Success');
            $('.small-model').find('.modal-body').html('<div class="text-success text-center"><i class="fa fa-check-circle"></i> '+callback.message+'</div>');
            $('.uploader').hide();
            $('.selector').show();
            $('.dropzone').hide();
            $('.editor-pallate').show();
            $(document).find('.closser').click();
            if(callback.gallary !=undefined && callback.gallary)
            {
              window.location=window.location;
            }  
            if(callback.about !=undefined && callback.about)
            {
              window.location=window.location;
            } 
          }
        else
        {
            $.each(callback.uform_errors,function(key,value)
            {
              el.find("input[aria-label='"+key+"'],textarea[aria-label='"+key+"'],select[aria-label='"+key+"']").addClass('is-invalid').parents('.form-group').find('.feedback').addClass('invalid-feedback').html('<i class="fa fa-exclamation-circle"></i> '+value);
            }); 
            $.each(callback.eform_errors,function(key,value)
            {
              el.find("input[aria-label='"+key+"'],textarea[aria-label='"+key+"'],select[aria-label='"+key+"']").addClass('is-invalid').parents('.form-group').find('.feedback').addClass('invalid-feedback').html('<i class="fa fa-exclamation-circle"></i> '+value);
            });
        }
      },
      error:function(err)
      {
        el.parents('.card,.editor').find('.overlay-close').addClass('btn-remove');
        el.find('button').html(btn_text).attr('disabled',false);
        el.parents('.card,.editor').find('.load-overlay .loader-container').html('<span class="text-danger font-weight-bold"> <i class="fa fa-alert-triangle"></i> '+err.status+' :'+err.statusText+'</span>.');
      }
    });
  return false;
});

$(document).on('click','.del-data',function(e)
{
  e.preventDefault();
  var el=$(this);
  $('.delete-model').modal({show:true});
  $('.delete-model').find('.modal-title').text('Confirm');
  $('.delete-model').find('.modal-body').html('<div class="text-warning text-info text-center"><i class="fa fa-alert-triangle"></i> Confirm deleting item .</div> <div class="text-center"><button class="btn btn-secondary cancelBtn" >cancel</button><button data-host="'+el.data('host')+'" data-url="'+el.attr('href')+'" class="btn btn-danger confirmBtn">confirm</button></div>');
});

$(document).on('click','.cancelBtn',function()
{
  $(this).parents('.modal').find('.close').click();
});

$(document).on('click','.confirmBtn',function()
{
  var el=$(this),
  url=el.data('url');
  $.ajax(
      {
        url:url,
        dataType:'json',
        beforeSend:function()
        {
          el.html('<i class="spinner-border spinner-border-sm" role="status"></i> Please wait...');
        },
        success:function(callback)
        {
          el.html('confirm');
          refreshPage(el,el.data('host'),'table-results');
          $('.delete-model').modal('hide');
          if(callback.valid)
          {
            $('.small-model').modal('show');
            $('.small-model').find('.modal-title').text('Success');
            $('.small-model').find('.modal-body').html('<div class="text-success text-center"><i class="fa fa-check-circle"></i> '+callback.message+'.</div>');
          }
          else
          {
            $('.small-model').modal('show');
            $('.small-model').find('.modal-title').text('Warning');
            $('.small-model').find('.modal-body').html('<div class="text-warning text-center"><i class="fa fa-exclmation-circle"></i> '+callback.message+'</div>');
          }
        },
        error(err)
        {
          el.html('confirm');
          console.log(err.status+':'+err.statusText);
        }
      });
});

/*refreshPage*/
function refreshPage(wrapper,url, target)
{
    $.ajax(
    {
      url:url,
      context:this,
      dataType:'html',
      success:function(callback)
      {
        $(document).find('.'+target).html($(callback).find('.'+target).html());
        observerImages();
      },
      error:function(err)
      {
        console.log(err.status+':'+err.statusText);
      }
    });
}

$(document).ready(function()
{
    (function($) 
    {
        "use strict"
        $(document).on('click','.fixedHeader',function()
        {
          $('.h1').click();
          localStorage.fixedHeader=$('.h1').is(':checked');
          if(localStorage.getItem("fixedHeader") == 'true')
          {
            new quixSettings({
                headerPosition: "fixed"
            });
          }
        });

        if(localStorage.getItem("fixedHeader") == 'true')
        {
          new quixSettings({
              sidebarPosition: "fixed"
          });
        }

        $(document).on('click','.fixedSideBar',function()
        {
          $('.h2').click();
          localStorage.fixedSideBar=$('.h2').is(':checked');
          if(localStorage.getItem("fixedSideBar") == 'true')
          {
            new quixSettings({
                sidebarPosition: "fixed"
            });
          }
        }); 
        if(localStorage.getItem("fixedSideBar") == 'true')
        {
          new quixSettings({
              sidebarPosition: "fixed"
          });
        }

        $(document).on('click','.rtller',function()
        {
          $('.h3').click();
          localStorage.rtller=$('.h3').is(':checked');
          if(localStorage.getItem("rtller") == 'true')
          {
            new quixSettings({
                sidebarPosition: "rtl"
            });
          }
        }); 

        if(localStorage.getItem("rtller") == 'true')
        {
          new quixSettings({
              sidebarPosition: "rtl"
          });
        }

        $(document).on('click','.dark',function()
        {
          $('.h4').click();
          localStorage.dark=$('.h4').is(':checked');
          if(localStorage.getItem("dark") == 'true')
          {
            localStorage.light=false;
            new quixSettings({
                version: "dark"
            });
          }
        });

        if(localStorage.getItem("dark") == 'true')
        {
          localStorage.light=false;
          new quixSettings({
              version: "dark"
          });
        }
        $(document).on('click','.light',function()
        {
          $('.h5').click();
          localStorage.light=$('.h5').is(':checked');
          if(localStorage.getItem("light") == 'true')
          {
            localStorage.dark=false;
            new quixSettings({
                version: "light"
            });
          }
        });
        if(localStorage.getItem("light") == 'true')
        {
          localStorage.dark=false;
          new quixSettings({
              version: "light"
          });
        }
        
    
    })(jQuery);
});

$(document).on('change','input[type=file]',function()
{
  $(this).removeClass('is-invalid').addClass('is-valid').parent().find('label').removeClass('invalid-feedback').addClass('valid-feedback').html('Filename: '+this.files[0].name);
});