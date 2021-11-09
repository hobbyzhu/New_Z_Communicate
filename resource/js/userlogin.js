
// 个人页面标签切换
//注册页面 先移动二层标签  再先移动3层标签
// function showlogon(){
//     //先移动二层标签
//     $('#home-tab').removeClass('active');
//     $('#profile-tab').addClass('active');
//     $('#contact-tab').removeClass('active');
//     //移动3层标签 为实现
//
//     $('#admin').removeClass('active');
//     $('#edit').addClass('active');
//     $('#contact').removeClass('active');
//
//
//     $('#staticBackdrop').modal('show')
// }





//发送邮箱验证码
function doSendMail(obj) {
    var email = $.trim($('#regname').val())
    //对邮箱地址进行校验
    if(!email.match(/.+@.+\..+/)){
        window.alert('邮箱地址格式不正确')
        $('#regname').focus()
        return false
    }
    $.post('/ecode','email=' + email,function (date){
        // 这是后端验证的反馈
        if (date == 'email-invalid'){
            window.alert('邮箱地址格式不正确')
            $('#regname').focus()
            return false
        }
        if (date == 'email-pass'){
            window.alert('邮件已发送')
            $('#regname').attr('disabled',true)  // 验证码发送后禁止更改注册邮箱
            $(obj).attr('disabled',true)   // 验证码发送后发送button 禁止重复发送 obj对于的是this 也可以添加id
            return false
        }
        else {
            window.alert('邮件发送失败')
            $('#regname').focus()
            return false
        }
    })
}


// 用户注册验证
function dologon(e){
    if (e != null && e.keyCode !=13){
        return false;
    }
    var logonname = $.trim($('#regname').val())  //邮箱地址框获取值
    var logonpass = $.trim($('#regpass').val())  //密码地址获取值
    var logoncode = $.trim($('#regcode').val())  //邮箱验证码框获取值
    if (!logonname.match(/.+@.+\..+/) || logonpass.length < 5) {
        window.alert('注册邮箱不正确，或者密码少于5位')
        return false

    } else {
        // 构建post请求的正文数据
        var param = 'username=' + logonname;
        param += '&password=' + logonpass;
        param += '&ecode=' +logoncode;

        // 利用jQuery框架发送post请求，并获取到后台注册接口的响应内容  参数(后台端口， 正文 ，返回内容)
        $.post('/user', param, function (date){
            if (date == "ecode-error"){
                window.alert('验证码错误')
                $('#regname').val('')  //清除验证码框的内容
                $('#regname').focus()  //让证码框获得焦点，重新输入
            }
            else if (date =='up-invalind'){
                window.alert('邮箱地址错误或者密码少于5位')
            }
            else if(date == 'user- repeted'){
                window.alert('用户名已经注册')
                $('#regname').focus()  //获得焦点，重新输入
            }
            else if(date == 'reg-pass'){
                window.alert('注册成功')
                //注册成功后 ，延时1s 刷新当前页面
                setTimeout('location.reload();',1000)
            }
        });
    }
}
// 登录
function dologin(e){
    if (e != null && e.keyCode !=13){
        return false
    }
    var loginname = $.trim($('#loginname').val());
    var loginpass = $.trim($('#loginpass').val());
    var logincode = $.trim($('#logincode').val());

    // 可以完善的更加完美，此处简单判断
    if (loginname.length < 5 || loginpass.length < 5){
        window.alert('用户名或者密码少于5位')
        return  false
    }
    else {
        // 和注册一样，也是拼接字符串并进行post请求
       var param = 'username=' + loginname;
        param += '&password=' + loginpass;
        param += '&vcode=' +logincode;

        // 构建post请求
        $.post('/login', param, function (data){
            if (data == 'vcode-error'){
                window.alert('验证码错误')
                $('#logincode').val('') //清除验证码
                $("#logincode").focus() // 焦点回到输入框
            }
            else if (data == 'login-pass'){
                window.alert('登录成功')
                setTimeout('location.reload();',1000)
            }
            else if (data == 'login-fail'){
                window.alert('用户名或密码错误')
            }
        })
    }
}


//找回密码 1.发送邮箱验证码
function dofindpassword_SendMail(obj) {
    var email = $.trim($('#findname').val())
    //对邮箱地址进行校验
    if(!email.match(/.+@.+\..+/)){
        window.alert('邮箱地址格式不正确')
        $('#regname').focus()
        return false
    }
    $.post('/ecode','email=' + email,function (date){
        // 这是后端验证的反馈
        if (date == 'email-invalid'){
            window.alert('邮箱地址格式不正确')
            $('#regname').focus()
            return false
        }
        if (date == 'email-pass'){
            window.alert('邮件已发送')
            $('#findname').attr('disabled',true)  // 验证码发送后禁止更改注册邮箱
            $(obj).attr('disabled',true)   // 验证码发送后发送button 禁止重复发送 obj对于的是this 也可以添加id
            return false
        }
        else {
            window.alert('邮件发送失败')
            $('#regname').focus()
            return false
        }
    })
}

// 找回密码2
function findpassword(e){
    if (e != null && e.keyCode !=13){
        return false;
    }
    var findname = $.trim($('#findname').val())  //邮箱地址框获取值
    var findpass = $.trim($('#findpass').val())  //密码地址获取值
    var findcode = $.trim($('#findcode').val())  //邮箱验证码框获取值
    if (!findname.match(/.+@.+\..+/) || findpass.length < 5) {
        window.alert('注册邮箱不正确，或者密码少于5位')
        return false

    } else {
        // 构建post请求的正文数据
        var param = 'username=' + findname;
        param += '&newpassword=' + findpass;
        param += '&ecode=' +findcode;

        // 利用jQuery框架发送post请求，并获取到后台注册接口的响应内容  参数(后台端口， 正文 ，返回内容)
        $.post('/repassword', param, function (date){
            if (date == "ecode-error"){
                window.alert('验证码错误')
                $('#findcode').val('')  //清除验证码框的内容
                $('#findcode').focus()  //让证码框获得焦点，重新输入
            }
            else if (date =='up-invalind'){
                window.alert('邮箱地址错误或者密码少于5位')
            }
            else if(date == 'user-unlogin'){
                window.alert('用户名未注册')
                $('#findname').focus()  //获得焦点，重新输入
            }
            else if(date == 'password-reset'){
                window.alert('密码已经更改')
                //注册成功后 ，延时1s 刷新当前页面
                setTimeout('location.reload();',1000)
            }
        });
    }
}