const progressPrefix = 'bachataClub:progress:';
const lessonCards = Array.from(document.querySelectorAll('[data-lesson-card]'));

function storageAvailable() {
    try {
        const probeKey = '__storage_probe__';
        localStorage.setItem(probeKey, '1');
        localStorage.removeItem(probeKey);
        return true;
    } catch (error) {
        return false;
    }
}

const canUseStorage = storageAvailable();

function getProgressKey(slug) {
    return `${progressPrefix}${slug}`;
}

function getProgress(slug) {
    if (!canUseStorage) {
        return 0;
    }

    const value = Number(localStorage.getItem(getProgressKey(slug)) || 0);
    return Number.isFinite(value) ? value : 0;
}

function setProgress(slug, seconds) {
    if (!canUseStorage) {
        return;
    }

    if (seconds > 0) {
        localStorage.setItem(getProgressKey(slug), String(seconds));
        return;
    }

    localStorage.removeItem(getProgressKey(slug));
}

function updateProgressBar(card, currentTime, duration) {
    const progressBar = card.querySelector('.progress-bar');
    if (!progressBar) {
        return;
    }

    const percent = duration > 0 ? Math.min(100, (currentTime / duration) * 100) : 0;
    progressBar.style.width = `${percent}%`;
}

function bindVideoProgress(card) {
    const video = card.querySelector('video[data-lesson-slug]');
    if (!video) {
        return;
    }

    const slug = video.dataset.lessonSlug || '';
    if (!slug) {
        return;
    }

    video.addEventListener('loadedmetadata', () => {
        const savedProgress = getProgress(slug);
        if (savedProgress > 5 && Number.isFinite(video.duration) && savedProgress < video.duration - 5) {
            video.currentTime = savedProgress;
        }

        updateProgressBar(card, video.currentTime, video.duration || 0);
    });

    video.addEventListener('timeupdate', () => {
        if (!Number.isFinite(video.duration) || video.duration <= 0) {
            return;
        }

        setProgress(slug, video.currentTime);
        updateProgressBar(card, video.currentTime, video.duration);
    });

    video.addEventListener('ended', () => {
        setProgress(slug, 0);
        updateProgressBar(card, video.duration || 0, video.duration || 0);
    });
}

lessonCards.forEach((card) => {
    bindVideoProgress(card);
});
