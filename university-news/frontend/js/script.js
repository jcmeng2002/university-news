// ===== 新增的交互功能 =====

// 1. 卡片悬停效果
function setupCardHoverEffects() {
    const cards = document.querySelectorAll('.news-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
            card.style.boxShadow = 'var(--shadow-xl)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'var(--shadow-md)';
        });
    });
}

// 2. 文本截断功能
function applyTextTruncation() {
    document.querySelectorAll('.news-summary').forEach(summary => {
        const lineHeight = 22; // 假设行高
        const maxHeight = lineHeight * 3;
        
        if (summary.scrollHeight > maxHeight) {
            const text = summary.textContent;
            let truncatedText = text;
            
            while (summary.scrollHeight > maxHeight && truncatedText.length > 10) {
                truncatedText = truncatedText.slice(0, -1);
                summary.textContent = truncatedText + '...';
            }
        }
    });
}

// 3. 在DOMContentLoaded中调用
document.addEventListener('DOMContentLoaded', function() {
    // 原有的初始化代码...
    
    // 添加这些调用
    setTimeout(() => {
        setupCardHoverEffects();
        applyTextTruncation();
    }, 500);
    
    // 添加搜索框防抖
    const searchInput = document.getElementById('search-input');
    let timeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            performSearch();
        }, 300);
    });
});