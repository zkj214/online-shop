var UpdateBtns=document.getElementsByClassName("update-cart")

for (var i=0;i < UpdateBtns.length;i++)
{
    UpdateBtns[i].addEventListener("click",function(){
        var productID=this.dataset.product;
        var action = this.dataset.action;
        console.log("Product ID: "+productID+" Action: "+action)

        console.log("USER: " + user)
        if(user === "AnonymousUser")
        {
            console.log("User is not authenticated");
        }
        else
        {
            UpdateUserOrder(productID,action)
        }
    })

}

function UpdateUserOrder(productID,action)
{
    console.log("User is authenticated. Sending data...")

    var  url="/update_cart/"

    fetch(url,{
        method:"POST",
        headers:{
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body:JSON.stringify({"productId":productID,"action":action})
    })
    .then((response) => {return response.json()})
    .then((data) => {location.reload()})
}

var searchbox=document.getElementById("searchbox")
searchbox.addEventListener("click",function(){
    this.style.background="#fff";
    this.style.color="#000";
})

var container=document.querySelector(".container")
container.addEventListener("click",function(){
    searchbox.style.background="#37474F";
    searchbox.style.color="#fff";
})