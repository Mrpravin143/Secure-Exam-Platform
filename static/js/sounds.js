
function playSound(soundFile) {
    const audio = new Audio(soundFile);
    audio.volume = 0.4;   // professional volume
    audio.play().catch(err => {
        console.log("Autoplay blocked:", err);
    });
}

