let websocket_connection = null;

const min_pass = 8;

function searchUser(){
    const token = localStorage.getItem('token');
    const email = document.getElementById('search_user').value;

    if (email === "") {
        document.getElementById('search_error').textContent = "email cannot be empty";
        return false;
    }

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/get_user_data_by_email/' + email, true);
        xhr.setRequestHeader('Authorization', token);

        xhr.onload = function () {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText)

                if (response.success === false){
                    errormessage.textContent = response.message;
                }
                else{
                    document.getElementById('browse').style.display = 'none';
                    document.getElementById('browse_result').style.display = 'block';
                
                    const userData = response.data;
                    document.getElementById('browse_info').innerHTML = "<p>Email: " + userData.email + "</p>" +
                    "<p>First Name: " + userData.firstname + "</p>" +
                    "<p>Family Name: " + userData.familyname + "</p>" +
                    "<p>Gender: " + userData.gender + "</p>" +
                    "<p>City: " + userData.city + "</p>" +
                    "<p>Country: " + userData.country + "</p>";
                
                    loadBrowseWall();
                }

            }
            else {
                errormessage.textContent = 'Server error status: ' + xhr.status;
            }
        }
        xhr.onerror = () => errormessage.textContent = "network error";
        xhr.ontimeout = () => errormessage.textContent = "request time out error";

        xhr.send();
    } catch (error) {
        errormessage.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function loadBrowseWall(){
    const email = document.getElementById('search_user').value;
    const token = localStorage.getItem('token');
    const errormessage = document.getElementById('browse_wall_error');

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/get_user_messages_by_email/' + email, true);
        xhr.setRequestHeader('Authorization', token);

        xhr.onload = function () {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText)

                if (response.success === false){
                    errormessage.textContent = response.message;
                }
                else{
                    const messages = response.data;
                    const messageWall = document.getElementById('browse_wall_messages');
                    let content = "<hr>";
                    messages.forEach(message => {
                        content += "<p>" + message.content + "</p><hr>";
                    });
                    messageWall.innerHTML = content;                    
                }

            }
            else {
                errormessage.textContent = 'Server error status: ' + xhr.status;
            }
        }
        xhr.onerror = () => errormessage.textContent = "network error";
        xhr.ontimeout = () => errormessage.textContent = "request time out error";

        xhr.send();
    } catch (error) {
        errormessage.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function postBrowseMessage(){
    const token = localStorage.getItem('token');
    const message = document.getElementById('browse_message').value;
    const email = document.getElementById('search_user').value;
    //serverstub.postMessage(token, message, email)
    const errormessage = document.getElementById('browse_post_error');

    if(message.trim() === ""){
        errormessage.textContent = "message cannot be empty";
        return false;
    }

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/post_message', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('Authorization', token);

        xhr.onload = function () {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText)

                if (response.success === false){
                    errormessage.textContent = response.message;
                }
                else{
                    errormessage.textContent = "message posted!";
                }

            }
            else {
                errormessage.textContent = 'Server error status: ' + xhr.status;
            }
        }
        xhr.onerror = () => errormessage.textContent = "network error";
        xhr.ontimeout = () => errormessage.textContent = "request time out error";

        data = {
            message: message,
            email: email
        }
        xhr.send(JSON.stringify(data));
    } catch (error) {
        errormessage.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function loadWall(){
    const token = localStorage.getItem('token');
    const errormessage = document.getElementById('wall_error');

    if (!token){
        errormessage.textContent = "Invalid user";
    }

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/get_user_messages_by_token', true);
        xhr.setRequestHeader('Authorization', token);

        xhr.onload = function () {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText);

                if (response.success === false){
                    errormessage.textContent = response.message;
                }
                else{
                    const messageWall = document.getElementById('wall_messages');
                    messages = response.data;

                    let content = "<hr>";
                    messages.forEach(message => {
                        content += "<p>" + message.content + "</p><hr>";
                    });
                    messageWall.innerHTML = content;
                    
                }

            }
            else {
                errormessage.textContent = 'Server error status: ' + xhr.status;
            }
        }

        xhr.onerror = () => errormessage.textContent = "network error";
        xhr.ontimeout = () => errormessage.textContent = "request time out error";
    
        xhr.send();
    } catch (error) {
        errormessage.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function postMessage(){
    const token = localStorage.getItem('token');
    const message = document.getElementById('message').value;
    //serverstub.postMessage(token, message, email)
    const errormessage = document.getElementById('post_message_error');

    if(message.trim() === ""){
        errormessage.textContent = "message cannot be empty";
        return false;
    }

    try {
        const xhr1 = new XMLHttpRequest();
        xhr1.open('GET', '/get_user_data_by_token', true);
        xhr1.setRequestHeader('Authorization', token);

        xhr1.onload = function () {
            if (xhr1.status === 200){
                const response1 = JSON.parse(xhr1.responseText)

                if (response1.success === false){
                    errormessage.textContent = response1.message;
                }
                else{
                    const email = response1.data.email;
                    const xhr2 = new XMLHttpRequest();

                    xhr2.open('POST', '/post_message', true);
                    xhr2.setRequestHeader('Authorization', token);
                    xhr2.setRequestHeader('Content-Type', 'application/json');

                    xhr2.onload = function() {
                        if(xhr2.status === 200){
                            const response2 = JSON.parse(xhr2.responseText);

                            if(response2.success === false){
                                errormessage.textContent = response2.message;
                            }
                            else{
                                errormessage.textContent = "Message posted!";
                            }
                        }
                        else{
                            errormessage.textContent = 'Server error status2: ' + xhr2.status;
                        }
                    }

                    const data = {
                        email: email,
                        message: message
                    }

                    xhr2.onerror = () => errormessage.textContent = "network error2";
                    xhr2.ontimeout = () => errormessage.textContent = "request time out error2";

                    xhr2.send(JSON.stringify(data));
                }

            }
            else {
                errormessage.textContent = 'Server error status: ' + xhr1.status;
            }
        }
        xhr1.onerror = () => errormessage.textContent = "network error";
        xhr1.ontimeout = () => errormessage.textContent = "request time out error";

        xhr1.send();
    } catch (error) {
        errormessage.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function isValidSignIn(event) {
    event.preventDefault();

    const email = document.getElementById('login_email');
    const password = document.getElementById('login_password');
    const error_message = document.getElementById('error_login');
    error_message.textContent = '';

    try {
        if (password.value.length < min_pass) {
            error_message.textContent = `password must have at least 8 chars`;
            return false;
        }   
        
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/sign_in', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText)

                if (response.success === false){
                    error_message.textContent = response.message;
                }
                else{
                    localStorage.setItem('token', response.data);
                    updateView();
                }
            }  
            else {
                error_message.textContent = 'Server error status: ' + xhr.status;
            }   
        };

        xhr.onerror = () => error_message.textContent = "network error";
        xhr.ontimeout = () => error_message.textContent = "request time out error";

        const data = {
            username: email.value,
            password: password.value
        }
        xhr.send(JSON.stringify(data));

    } catch (error) {
        error_message.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function isValidSignUp(event) {
    event.preventDefault();  

    const email = document.getElementById('signup_email');
    const password = document.getElementById('signup_password');
    const repeatPassword = document.getElementById('signup_repeat_password');
    const firstname = document.getElementById('firstname');
    const familyname = document.getElementById('familyname');
    const gender = document.getElementById('gender');
    const city = document.getElementById('city');
    const country = document.getElementById('country');

    const error_message = document.getElementById('error_signup');
    error_message.textContent = '';

    try {
        if (password.value.length < min_pass) {
            error_message.textContent = "password must have at leats 8 chars";
            return false;
        }
    
        if (password.value !== repeatPassword.value) {
            error_message.textContent = "passwords must be the same";
            return false;
        }  
        
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/sign_up', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function () {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText)

                if (response.success === false){
                    error_message.textContent = response.message;
                }
                else{
                    error_message.textContent = "registered!";
                }
            }  
            else {
                error_message.textContent = 'Server error status: ' + xhr.status;
            }   
        };

        xhr.onerror = () => error_message.textContent = "network error";
        xhr.ontimeout = () => error_message.textContent = "request time out error";

        const dataObj = {
            email: email.value,
            password: password.value,
            firstname: firstname.value,
            familyname: familyname.value,
            gender: gender.value,
            city: city.value,
            country: country.value
        };

        xhr.send(JSON.stringify(dataObj));

    } catch (error) {
        error_message.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

//function for changing password
function isValidPassword(event) {
    event.preventDefault();

    const oldPassword = document.getElementById('old_password');
    const newPassword = document.getElementById('new_password');
    const newPasswordRepeat = document.getElementById('new_password_repeat');
    
    const error_message_acc = document.getElementById('error_tab_account');
    error_message_acc.textContent = '';

    if (newPassword.value.length < min_pass) {
        error_message_acc.textContent = "password must have at leats 8 chars";
        return false;
    }

    if (newPassword.value !== newPasswordRepeat.value) {
        error_message_acc.textContent = "passwords must be the same";
        return false;
    }

    const token = localStorage.getItem('token');

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('PUT', '/change_password', true);
        xhr.setRequestHeader('Authorization', token);

        xhr.onload = function () {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText)

                if (response.success === false){
                    error_message_acc.textContent = response.message;
                }
                else{
                    error_message_acc.textContent = "password has changed!";            
                }

            }
            else {
                error_message_acc.textContent = 'Server error status: ' + xhr.status;
            }
        }
        xhr.onerror = () => error_message_acc.textContent = "network error";
        xhr.ontimeout = () => error_message_acc.textContent = "request time out error";

        const data = {
            oldpassword: oldPassword,
            newpassword: newPassword
        }

        xhr.send(JSON.stringify(data));
    } catch (error) {
        error_message_acc.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function signOut(){
    //serverstub.signOut(token)
    //const response = serverstub.signOut(localStorage.getItem('token'));
    const token = localStorage.getItem('token');
    const error_message = document.getElementById('logout_message');

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('DELETE', '/sign_out', true);
        xhr.setRequestHeader('Authorization', token);

        xhr.onload = function () {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText)

                if (response.success === false){
                    error_message.textContent = response.message;
                }
                else{
                    localStorage.removeItem('token');
                    document.getElementById('viewContent').innerHTML = document.getElementById('welcomeview').innerHTML;
                }

            }
            else {
                error_message.textContent = 'Server error status: ' + xhr.status;
            }
        }
        xhr.onerror = () => error_message.textContent = "network error";
        xhr.ontimeout = () => error_message.textContent = "request time out error";

        xhr.send();
    } catch (error) {
        error_message.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

function initWebsocket(token){

    try {
        if (websocket_connection){
            websocket_connection.close();
        }

        websocket_connection = new WebSocket('http://' + window.location.host + '/ws?token=' + token);

        websocket_connection.onmessage = function(e) {
            if(e.data === 'logout'){
                localStorage.removeItem('token');
                websocket_connection.close();
                document.getElementById('viewContent').innerHTML = document.getElementById('welcomeview').innerHTML;
                window.alert("You have logged in another session.");
            }
        }

    } catch (error) {
        console.log("Something wrong happened: " + error);
    }
}

function updateView(){
    const token = localStorage.getItem('token');
    
    if (token === null) {
        document.getElementById('viewContent').innerHTML = document.getElementById('welcomeview').innerHTML;
    }
    else{
        document.getElementById('viewContent').innerHTML = document.getElementById('profileview').innerHTML;
        initTabs();
        initWebsocket(token);
    }
}

//function for getting and loading the personal info of the client
function loadInfo(){
    const token = localStorage.getItem('token');
    const errormessage = document.getElementById('home_error');

    try {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/get_user_data_by_token', true);
        xhr.setRequestHeader('Authorization', token);

        xhr.onload = function () {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText);
                console.log(response.message);

                if (response.success === false){
                    errormessage.textContent = response.message;
                }
                else{
                    let content = "";
                    content += "<p>Email: " + response.data.email + "</p>";
                    content += "<p>First Name: " + response.data.firstname + "</p>";
                    content += "<p>Family Name: " + response.data.familyname + "</p>";
                    content += "<p>Gender: " + response.data.gender + "</p>";
                    content += "<p>City: " + response.data.city + "</p>";
                    content += "<p>Country: " + response.data.country + "</p>";
            
                    document.getElementById('profile_info').innerHTML = content;
                }

            }
            else {
                errormessage.textContent = 'Server error status: ' + xhr.status;
            }
        }

        xhr.onerror = () => errormessage.textContent = "network error";
        xhr.ontimeout = () => errormessage.textContent = "request time out error";
    
        xhr.send();
    } catch (error) {
        errormessage.textContent = "Something went wrong";
        console.error(error);
        return false;
    }
}

//fuction for profileview
function initTabs(){
    const tabs = document.querySelectorAll('.tabopt');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const panels = document.querySelectorAll('.tabcontent .tab');
            panels.forEach(panel => {
                panel.style.display = 'none';
            });

            const chosenPanelId = tab.getAttribute('data-target');
            const chosenPanel = document.getElementById(chosenPanelId);
            chosenPanel.style.display = 'block';
        });
    });

    loadInfo();
    loadWall();

}