const socket = io("localhost:8080/", {
    reconnectionDelayMax: 10000,
    auth: {
        token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJmaXJzdF9uYW1lIjoic3RyaW5nIiwibGFzdF9uYW1lIjoic3RyaW5nIiwiZXhwaXJlcyI6MTcyMTgwNTI3My42OTM3MTR9.8QeNTbVW6XdL0P0kKb8s9bbfUGrQCQv_hWOtC4fSDGs"
    }
})

socket.on("/auth/verify", data => {
    console.log(data)
})


socket.on("broadcast", data => {
    console.log(data)
})
