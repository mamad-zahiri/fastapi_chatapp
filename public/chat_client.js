const elmt_token = document.getElementById("token")

const elmt_message_list = document.getElementById("message_list")
const elmt_user_list = document.getElementById("user_list")
const elmt_onlne_user_list = document.getElementById("online_user_list")

const elmt_group_list = document.getElementById("group_list")

const get_token = () => {
    return elmt_token.value
}

let socket = io("localhost:8080/", {
    reconnectionDelayMax: 10000,
    auth: { token: get_token() },
})

const connect = () => {
    socket = io("localhost:8080/", {
        reconnectionDelayMax: 10000,
        auth: { token: get_token() },
    })
}

socket.on("/private/chat", msg => {
    const txt = `
    <div style="border-bottom: 2px solid black;">
    <b><span style="color: green;">sender:</span></b> ${msg.sender}<br/>
    <b>msg:</b> ${msg.message}<br/>
    <b><span style="color: blue;">at:</span></b> ${msg.timestamp}<br/>
    </div>
    `

    const li = document.createElement("li");
    li.innerHTML = txt

    elmt_message_list.appendChild(li);
})


socket.on("/broadcast/user-disconnect", data => {
    console.log("-".repeat(40))
    console.log(`broadcast: ${data}`)
})



const list_private_chats = () => {
    payload = {
        token: get_token(),
    }

    socket.emit("/private/list-chats", payload, res => {
        console.log(res)
    })
}

const list_new_private_chats = () => {
    payload = {
        token: get_token(),
    }

    socket.emit("/private/list-new-chats", payload, res => {
        console.log(res)
    })
}

const send_message = () => {
    const to = document.getElementById("to")
    const msg = document.getElementById("msg")

    payload = {
        token: get_token(),
        receiver: to.value,
        message: msg.value
    }

    socket.emit("/private/chat", payload, res => {
        console.log(res)

        to.value = ""
        msg.value = ""
    })
}


const list_users = () => {
    socket.emit("/system/list-users", users => {
        elmt_user_list.innerHTML = ""

        for (obj in users) {
            const user = users[obj]
            const txt = `
            <div style="border-bottom: 2px solid black">
            id: ${user.id}<br/>
            email: ${user.email}<br/>
            name: ${user.first_name} ${user.last_name}<br/>
            last seen: ${user.last_seen}
            </div>
            `

            elmt_user_list.innerHTML += txt
        }

    })
}

const list_online_users = () => {
    socket.emit("/system/list-online-users", users => {
        elmt_onlne_user_list.innerHTML = ""

        for (user of users) {
            const txt = `
            <div style="border-bottom: 2px solid black">
            ${user}
            </div>
            `

            elmt_onlne_user_list.innerHTML += txt
        }

    })
}


const list_groups = () => {
    socket.emit("/group/list-groups", groups => {
        elmt_group_list.innerHTML = ""

        for (obj in groups) {
            const group = groups[obj]
            const txt = `
            <div style="border-bottom: 2px solid black">
            id: ${group.id}<br/>
            name: ${group.name}<br/>
            </div>
            `

            elmt_group_list.innerHTML += txt
        }

    })
}

