class UIManager {
    constructor() {
        // UI 元素
        this.darkModeToggle = document.getElementById('darkModeToggle');
        this.lightIcon = document.getElementById('lightIcon');
        this.darkIcon = document.getElementById('darkIcon');
        this.error = document.getElementById('error');
        this.loading = document.getElementById('loading');
        this.progressBar = this.loading.querySelector('.progress-bar');
        this.progressMessage = document.getElementById('progressMessage');
        this.scanCompleteToast = new bootstrap.Toast(document.getElementById('scanCompleteToast'));

        // NSFW 相关元素
        this.nsfwToggle = document.getElementById('nsfwToggle');
        this.nsfwIcon = document.getElementById('nsfwIcon');
        this.nsfwText = document.getElementById('nsfwText');
        this.showNSFW = false;

        // 初始化事件监听
        this.initEventListeners();
        this.initDarkMode();
    }

    // 初始化事件监听
    initEventListeners() {
        // 暗黑模式切换
        this.darkModeToggle.addEventListener('click', () => {
            const isDark = document.documentElement.getAttribute('data-bs-theme') !== 'dark';
            this.updateDarkModeUI(isDark);
        });

        // NSFW 切换
        this.nsfwToggle.addEventListener('click', () => {
            this.updateNSFWButton(!this.showNSFW);
        });
    }

    // 初始化暗黑模式
    initDarkMode() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.updateDarkModeUI(true);
        }
    }

    // 更新暗黑模式 UI
    updateDarkModeUI(isDark) {
        document.documentElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
        this.lightIcon.classList.toggle('d-none', isDark);
        this.darkIcon.classList.toggle('d-none', !isDark);
    }

    // 更新 NSFW 按钮状态
    updateNSFWButton(show) {
        this.showNSFW = show;
        if (show) {
            this.nsfwToggle.classList.remove('btn-success');
            this.nsfwToggle.classList.add('btn-danger');
            this.nsfwIcon.classList.remove('bi-eye-slash-fill');
            this.nsfwIcon.classList.add('bi-eye-fill');
            this.nsfwText.textContent = 'NSFW 已开启';
        } else {
            this.nsfwToggle.classList.remove('btn-danger');
            this.nsfwToggle.classList.add('btn-success');
            this.nsfwIcon.classList.remove('bi-eye-fill');
            this.nsfwIcon.classList.add('bi-eye-slash-fill');
            this.nsfwText.textContent = 'NSFW 已关闭';
        }
        // 触发 NSFW 状态更改事件
        document.dispatchEvent(new CustomEvent('nsfwStateChanged', { detail: show }));
    }

    // 显示错误信息
    showError(message) {
        this.error.textContent = message;
        this.error.classList.remove('d-none');
        setTimeout(() => {
            this.error.classList.add('d-none');
        }, 3000);
    }

    // 显示加载状态
    showLoading() {
        this.loading.classList.remove('d-none');
    }

    // 隐藏加载状态
    hideLoading() {
        this.loading.classList.add('d-none');
    }

    // 更新进度
    updateProgress(progress, message) {
        const progressPercent = Math.round(progress * 100);
        this.progressBar.style.width = `${progressPercent}%`;
        this.progressBar.setAttribute('aria-valuenow', progressPercent);
        this.progressBar.textContent = `${progressPercent}%`;
        this.progressMessage.textContent = message;

        if (progressPercent === 100) {
            setTimeout(() => {
                this.scanCompleteToast.show();
                this.hideLoading();
            }, 500);
        }
    }

    // 获取 NSFW 状态
    getNSFWState() {
        return this.showNSFW;
    }
}

export default new UIManager(); 