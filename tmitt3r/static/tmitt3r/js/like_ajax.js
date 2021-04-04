'use strict';
function tm33tLikeAjax(obj) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            // Likeのハートのスタイルを切り替える
            toggleHeartStyle(obj);
        }
    }
    // POSTするデータの作成
    let tm33tPk = obj.dataset.tm33tPk;
    let postState = '';
    const URL = '/tm33t/like/';
    // stateを切り替える
    if (obj.dataset.state === 'like') {
        postState = 'unlike';
    } else {
        postState = 'like';
    }
    let data = `like=${postState}&pk=${tm33tPk}`;
    // csrfトークンをクッキーから取得
    const csrftoken = getCookie('csrftoken');
    // headerを設定
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

    xhr.open('POST', URL, true);
    xhr.send(data);
}

function toggleTm33tLike(obj) {
    if (obj.dataset.state === 'like') {
        obj.dataset.state = 'unlike';
        obj.classList.remove('like');
        obj.classList.remove('fas');
        obj.classList.add('far');

    } else {
        obj.dataset.state === 'unlike';
        obj.classList.add('like');
        obj.classList.remove('far');
        obj.classList.add('fas');
    }
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}