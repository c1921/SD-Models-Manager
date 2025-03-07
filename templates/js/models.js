class ModelDisplayManager {
    constructor() {
        this.modelsList = document.getElementById('modelsList');
    }

    // 显示模型列表
    displayModels(models) {
        this.modelsList.innerHTML = models.map(model => this.generateModelCard(model)).join('');

        // 添加点击事件监听
        this.modelsList.querySelectorAll('.model-card').forEach(card => {
            card.addEventListener('click', () => {
                const modelData = JSON.parse(card.dataset.model);
                this.showModelDetail(modelData);
            });
        });
    }

    // 生成模型卡片 HTML
    generateModelCard(model) {
        const imgSrc = model.preview_url?.startsWith('/static') ?
            model.preview_url :
            '/static/images/' + model.preview_url?.split('/').pop();

        return `
        <div class="col">
            <div class="card h-100 model-card" data-model='${JSON.stringify(model)}'>
                <div class="row g-0 h-100">
                    ${model.preview_url ? `
                    <div class="col-4 col-sm-12">
                        <div class="card-img-container h-100">
                            <img
                                src="${imgSrc}"
                                alt="${model.name}"
                                onerror="this.onerror=null; this.src='${model.preview_url}';"
                                class="rounded-start rounded-sm-top"
                                style="cursor: pointer"
                            >
                        </div>
                    </div>
                    ` : ''}
                    <div class="col-8 col-sm-12">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title fw-bold mb-0" title="${model.name}">${model.name}</h5>
                                ${model.nsfw ? '<span class="badge text-bg-danger">NSFW</span>' : ''}
                            </div>
                            <p class="card-text">
                                <small class="d-block">类型: ${model.type}</small>
                                <small class="d-block">基础模型: ${model.baseModel || '未知'}</small>
                            </p>
                            ${model.url ? `<a href="${model.url}" class="btn btn-outline-secondary btn-sm" target="_blank">查看详情</a>` : ''}
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
                ${model.url ? `
                    <a href="${model.url}" class="btn btn-outline-secondary btn-sm mt-2" target="_blank">
                        <i class="bi bi-box-arrow-up-right me-1"></i>查看详情
                    </a>
                ` : ''}
            </div>
            `;

        // 显示模态框
        modal.show();
    }
}

export default new ModelDisplayManager(); 