// 筛选器配置
const filters = [
    {
        id: 'baseModel',
        name: '基础模型',
        getValues: (models) => new Set(models.map(model => model.baseModel || '未知'))
    },
    {
        id: 'type',
        name: '类型',
        getValues: (models) => new Set(models.map(model => model.type || '未知'))
    }
];

class FilterManager {
    constructor() {
        this.currentFilters = {
            baseModel: new Set(),
            type: new Set()
        };
    }

    // 生成筛选器 HTML
    generateFilterHTML(filter, values) {
        return `
        <div class="mb-3">
            <div class="nav flex-column">
                <div class="nav-item">
                    <p class="mt-3">${filter.name}</p>
                    <div class="d-flex flex-wrap gap-2" id="${filter.id}Filters">
                        <button type="button" class="btn btn-outline-success btn-sm" data-filter="${filter.id}" data-value="">
                            全部
                        </button>
                        ${Array.from(values).map(value => `
                            <button type="button" class="btn btn-outline-secondary btn-sm" data-filter="${filter.id}" data-value="${value}">
                                ${value}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
        `;
    }

    // 更新筛选器选项
    updateFilterOptions(models, filterContainer, filterContainerMobile) {
        // 清空容器
        filterContainer.innerHTML = '';
        filterContainerMobile.innerHTML = '';

        // 为每个筛选器生成 HTML
        filters.forEach(filter => {
            const values = filter.getValues(models);
            const filterHTML = this.generateFilterHTML(filter, values);

            // 添加到桌面端和移动端
            filterContainer.innerHTML += filterHTML;
            filterContainerMobile.innerHTML += filterHTML;
        });

        // 重新添加事件监听
        document.querySelectorAll('[data-filter]').forEach(button => {
            button.addEventListener('click', (e) => this.handleFilterClick(e));
        });
    }

    // 处理筛选器点击
    handleFilterClick(e) {
        const filter = e.target.dataset.filter;
        const value = e.target.dataset.value;
        const filterGroup = e.target.closest('.d-flex');

        if (!value) {
            // 处理"全部"按钮
            filterGroup.querySelectorAll('button').forEach(btn => {
                btn.classList.remove('active', 'btn-success');
                btn.classList.add('btn-outline-secondary');
            });
            this.currentFilters[filter].clear();
            e.target.classList.add('active', 'btn-success');
            e.target.classList.remove('btn-outline-secondary');
        } else {
            // 处理其他按钮
            e.target.classList.toggle('active');
            const allButton = filterGroup.querySelector('[data-value=""]');

            if (e.target.classList.contains('active')) {
                e.target.classList.remove('btn-outline-secondary');
                e.target.classList.add('btn-success');
                this.currentFilters[filter].add(value);
                allButton.classList.remove('active', 'btn-success');
                allButton.classList.add('btn-outline-secondary');
            } else {
                e.target.classList.remove('btn-success');
                e.target.classList.add('btn-outline-secondary');
                this.currentFilters[filter].delete(value);

                // 如果没有选中项，自动选中"全部"
                if (this.currentFilters[filter].size === 0) {
                    allButton.classList.add('active', 'btn-success');
                    allButton.classList.remove('btn-outline-secondary');
                }
            }
        }

        // 触发筛选更新事件
        document.dispatchEvent(new CustomEvent('filtersUpdated'));
    }

    // 应用筛选器
    applyFilters(models, showNSFW = false) {
        let filteredModels = models;

        // 应用基础模型筛选
        if (this.currentFilters.baseModel.size > 0) {
            filteredModels = filteredModels.filter(model =>
                this.currentFilters.baseModel.has(model.baseModel || '未知')
            );
        }

        // 应用类型筛选
        if (this.currentFilters.type.size > 0) {
            filteredModels = filteredModels.filter(model =>
                this.currentFilters.type.has(model.type || '未知')
            );
        }

        // 应用 NSFW 过滤
        if (!showNSFW) {
            filteredModels = filteredModels.filter(model => !model.nsfw && model.nsfwLevel < 3);
        }

        return filteredModels;
    }
}

export default new FilterManager(); 