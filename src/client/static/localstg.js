function removeDataOnUnload(key) {
    window.addEventListener('beforeunload', () => {
        localStorage.removeItem(key);
    });
}