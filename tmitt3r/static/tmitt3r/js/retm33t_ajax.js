'use strict';
function retm33tAjax(obj) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Likeのハートのスタイルを切り替える
            toggleRetm33tIconStyle(obj)
        }
    }
    // POSTするデータの作成
    let tm33tPk = obj.dataset.tm33tPk;
    const RETM33T_URL = '/tm33t/retm33t/';
    const UNRETM33T_URL = '/tm33t/unretm33t/';
    let URL = '';
    if (obj.dataset.state === 'retm33ted') {
        URL = UNRETM33T_URL;
    } else {
        URL = RETM33T_URL;
    }
    let data = `pk=${tm33tPk}`;
    // csrfトークンをクッキーから取得
    const csrftoken = getCookie('csrftoken');
    xhr.open('POST', URL, true);
    // headerを設定
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')

    xhr.send(data);
}

function toggleRetm33tIconStyle(obj) {
    let heart = obj.firstElementChild;
    if (obj.dataset.state === 'retm33ted') {
        obj.dataset.state = 'unretm33ted';
        heart.classList.remove('retm33ted');
        heart.classList.add('unretm33ted');
        return;
    }
    obj.dataset.state = 'retm33ted';
    heart.classList.remove('unretm33ted');
    heart.classList.add('retm33ted');
}
function getCookie(name) {
    let cookieValue = null;
    if (!document.cookie || document.cookie == '') {
        return cookieValue;
    }
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
    }
    return cookieValue;
}
