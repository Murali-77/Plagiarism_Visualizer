var text = prompt('Enter Text : ');

if(text.length >= 20){
    // Re-assigning variable 'text' if it exceeds 20 characters .
    text = text.slice(0,20);
}

window.alert("You have written " + text.length + " characters, you have " + (20-text.length) + " characters left : " + text);

// other way around .

/*
var text = prompt('Enter Text : ');
var textUnder20 = text.slice(0,20);
window.alert(textUnder20);
*/