function trigger(element) {
    console.log(element.value)
    if (element.value == "") {
        console.log("bandid" + (element.parentNode.children.length - 2).toString(), element.name)
        let hi = document.getElementsByName("bandid" + (element.parentNode.children.length - 2).toString())[0]
        console.log(hi.name);
        hi.remove()
    } else if (element.getAttribute('data-changed') === "0") {
        let newElement = element.cloneNode(true);
        newElement.name = "bandid" + (element.parentNode.children.length - 1).toString();
        newElement.options[0].disabled = false;
        newElement.options[0].style = "";
        document.getElementById("singers").appendChild(newElement)
    }
    for (let i = 1; i < element.parentNode.children.length - 2; i++) {
        document.getElementsByName(`bandid${i}`)[0].disabled = false;
    }
    for (let i = 1; i < element.parentNode.children.length - 3; i++) {
        document.getElementsByName(`bandid${i}`)[0].disabled = true;
    }
}
function enable() {
    for (let i = 1; i < document.getElementById("singers").children.length - 1; i++) {
        document.getElementsByName(`bandid${i}`)[0].disabled = false;
    }
    return true;
}