news_state = false
async function getData(respond) {
    const url = base_url + respond;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }
  
      const json = await response.json();
      return json
    } catch (error) {
      return {
            new : false, 
            data : [
                {
                    link : '',
                    header : 'Ошибка',
                    data : 'Попробуйте перезагрузить страницу'
                }
            ]
        }
    }
  }
async function get_notifications() {
    respond = await getData('get-notifications');
    data = respond.data;
    news = respond.new;
    list = document.getElementById("notif-list");
    list.textContent = '';
    if (data.length == 0){
        var notif_data = document.createElement("div");
        notif_data.innerHTML = 
        '<p class="placeholder">пусто</p>';
        list.appendChild(notif_data);
    }
    for (x = 0; x < data.length; x++){
        var notif_data = document.createElement("div");
        notif_data.innerHTML = 
        '<a href="' + data[x].link + '"><div class="notification">' + 
        '<p class="header">' + data[x].header + '</p>' + 
        '<p class="data">' + data[x].data + '</p>' + 
        '</div></a>';
        list.appendChild(notif_data);
    }
    if (news && !news_state){
        notif_button.classList.add('notif-new');
        notif_button.src = '/static/icons/notifications-new.svg';
        news_state = news
    }
    if (!news && news_state){
        notif_button.classList.remove('notif-new');
        notif_button.src = '/static/icons/notifications.svg';
        news_state = news
    }
}

notif_button = document.getElementById('notif-button');
notif_popup = document.getElementById('notif-popup');

get_notifications();

function notifOpen(){
    get_notifications();
    notif_button.classList.remove('notif-new');
}

var isNotifOpen = false
document.addEventListener('click', (e) => {
    if(e.target === notif_button) { 
        if (!isNotifOpen)
            notif_popup.classList.add('notif-activ');
        else
            notif_popup.classList.remove('notif-activ');
        isNotifOpen = !isNotifOpen;
        notifOpen()
    }
    else {
        notifOpen = false
        notif_popup.classList.remove('notif-activ');
    }
});


regular_chek = setInterval(get_notifications, 5000)