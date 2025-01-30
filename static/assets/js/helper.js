// Function to toggle the theme and save it to local storage
function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

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
