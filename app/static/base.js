const duration = 30;

function reloadPage() {
    console.log("Reloading...");
    window.location.reload();
}

function waitAndReload() {
    console.log("Reloading after " + duration + " seconds");
    setTimeout(() => reloadPage(), (duration * 1000));
}

window.onload = waitAndReload();