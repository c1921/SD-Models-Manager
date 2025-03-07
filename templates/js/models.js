class ModelDisplayManager {
    constructor() {
        this.modelsList = document.getElementById('modelsList');
    }

    // 处理复制按钮点击
    handleCopyClick(btn, filename) {
        navigator.clipboard.writeText(filename)
            .then(() => {
                // 临时改变按钮样式表示复制成功
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check"></i>';
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-success');
                
                setTimeout(() => {
                    btn.innerHTML = originalHtml;
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-secondary');
                }, 1000);
            })
            .catch(err => console.error('复制失败:', err));
    }

    // 显示模型列表
    displayModels(models) {
        this.modelsList.innerHTML = models.map(model => this.generateModelCard(model)).join('');

        // 仅在点击图片时触发模态窗口
        this.modelsList.querySelectorAll('.model-card img').forEach(img => {
            img.addEventListener('click', (event) => {
                const card = event.target.closest('.model-card');
                const modelData = JSON.parse(card.dataset.model);
                this.showModelDetail(modelData);
            });
        });

        // 添加复制按钮事件监听
        this.modelsList.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (event) => {
                this.handleCopyClick(btn, btn.dataset.filename);
            });
        });
    }


    // 生成模型卡片 HTML
    generateModelCard(model) {
        const imgSrc = model.preview_url?.startsWith('/static') ?
            model.preview_url :
            '/static/images/' + model.preview_url?.split('/').pop();
        // 处理 Windows 和 Unix 风格的路径
        const fileName = model.path.replace(/\\/g, '/').split('/').pop();
        // 转义 JSON 字符串中的特殊字符
        const modelJson = JSON.stringify(model).replace(/"/g, '&quot;');

        return `
        <div class="col">
            <div class="card h-100 d-flex flex-column model-card" data-model="${modelJson}">
                <div class="row g-0 h-100">
                    ${model.preview_url ? `
                    <div class="col-4 col-sm-12">
                        <div class="position-relative d-flex align-items-center justify-content-center overflow-hidden ratio" style="--bs-aspect-ratio: 133%;">
                            <img
                                src="${imgSrc}"
                                alt="${model.name}"
                                onerror="this.onerror=null; this.src='${model.preview_url}';"
                                class="rounded-start rounded-sm-top w-100 h-100 object-fit-cover"
                                style="cursor: pointer"
                            >
                        </div>
                    </div>
                    ` : ''}
                    <div class="col-8 col-sm-12">
                        <div class="card-body flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title text-truncate fw-bold mb-0" title="${model.name}">${model.name}</h5>
                                ${model.nsfw ? '<span class="badge text-bg-danger">NSFW</span>' : ''}
                            </div>
                            <p class="card-text">
                                <small class="d-block">类型: ${model.type}</small>
                                <small class="d-block">基础模型: ${model.baseModel || '未知'}</small>
                            </p>
                            <div class="d-flex gap-2">
                                <button class="btn btn-outline-secondary btn-sm copy-btn" 
                                        data-filename="${fileName}" 
                                        title="复制文件名">
                                    <i class="bi bi-files"></i>
                                </button>
                                ${model.url ? `
                                <a href="${model.url}" 
                                   class="btn btn-outline-secondary btn-sm" 
                                   target="_blank"
                                   title="打开 Civitai">
                                    <i class="bi bi-box-arrow-up-right"></i>
                                   </a>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
    }


    // 显示模型详情
    showModelDetail(model) {
        const modal = new bootstrap.Modal(document.getElementById('modelDetailModal'));
        const modalTitle = document.getElementById('modelDetailModalLabel');
        const modalImage = document.getElementById('modelDetailImage');
        const modalInfo = document.getElementById('modelDetailInfo');
        // 处理文件名
        const fileName = model.path.replace(/\\/g, '/').split('/').pop();

        // 设置标题
        modalTitle.textContent = model.name;

        // 设置图片
        if (model.preview_url) {
            const imgSrc = model.preview_url.startsWith('/static') ?
                model.preview_url :
                '/static/images/' + model.preview_url.split('/').pop();

            modalImage.innerHTML = `
            <img
                src="${imgSrc}"
                alt="${model.name}"
                onerror="this.onerror=null; this.src='${model.preview_url}';"
                class="img-fluid rounded"
                style="width: 100%; height: auto; object-fit: contain;"
            >
            `;
        }

        // 设置详细信息
        modalInfo.innerHTML = `
            <div class="mb-3">
                ${model.nsfw ? '<span class="badge text-bg-danger mb-2">NSFW</span>' : ''}
                <p class="mb-2"><strong>类型:</strong> ${model.type}</p>
                <p class="mb-2"><strong>基础模型:</strong> ${model.baseModel || '未知'}</p>
                ${model.description ? `<p class="mb-2"><strong>描述:</strong> ${model.description}</p>` : ''}
                <div class="d-flex gap-2 mt-2">
                    <button class="btn btn-outline-secondary btn-sm copy-btn" 
                            data-filename="${fileName}" 
                            title="复制文件名">
                        <i class="bi bi-files"></i>
                    </button>
                    ${model.url ? `
                    <a href="${model.url}" 
                       class="btn btn-outline-secondary btn-sm" 
                       target="_blank"
                       title="打开 Civitai">
                        <i class="bi bi-box-arrow-up-right"></i>
                    </a>
                    ` : ''}
                </div>
            </div>
            `;

        // 添加复制按钮事件监听
        modalInfo.querySelector('.copy-btn')?.addEventListener('click', (event) => {
            this.handleCopyClick(event.currentTarget, event.currentTarget.dataset.filename);
        });

        // 显示模态框
        modal.show();
    }
}

export default new ModelDisplayManager(); 