function getPreferredTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function setTheme(theme) {
    console.log("set theme to " + theme)
    if (theme=="light") {
        lightTheme();
        return;
    }
    darkTheme()
}
function darkTheme(){
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');
}
function lightTheme(){
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
}
function toggleTheme() {
    console.log("toggle")
    localStorage.setItem('theme', localStorage.getItem('theme')==="dark" ? 'light' : 'dark');
    setTheme(localStorage.getItem('theme'));
}



if (localStorage.getItem('theme') === null) {
    localStorage.setItem('theme', getPreferredTheme());
}
setTheme(localStorage.getItem('theme'));



window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    if (event.matches) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
    setTheme(localStorage.getItem('theme'));
});


function toggleLang() {
    let current_path = window.location.pathname
    console.log(current_path)

    if (current_path.includes("/cs")) {
        current_path = current_path.replace("repozitare", "repos").replace("projekty", "projects").replace("projekt", "project").replace("nas-tym", "team")
        window.location.href = current_path.replace("/cs", "");
    } else {
        current_path = current_path.replace("repos", "repozitare").replace("projects", "projekty").replace("project", "projekt").replace("team", "nas-tym")
        window.location.href = "/cs" + current_path;
    }
}

window.onload = () => {
    document.getElementById('theme-toggle-1').addEventListener('click', () => {
        toggleTheme();
    });
    document.getElementById('theme-toggle-2').addEventListener('click', () => {
        toggleTheme();
    });

    document.getElementById('lang-toggle-1').addEventListener('click', () => {
        toggleLang();
    });
    document.getElementById('lang-toggle-2').addEventListener('click', () => {
        toggleLang();
    });

}
