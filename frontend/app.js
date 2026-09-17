// Render Items in fetchItems()
listEl.innerHTML = items.map(item => {
    let contentHtml = '';

    if (item.item_type === 'link') {
        contentHtml = `<a href="${escapeHtml(item.content)}" target="_blank" class="text-sky-400 hover:underline [word-break:break-word]">${escapeHtml(item.content)}</a>`;
    } else if (item.item_type === 'image') {
        contentHtml = `
            <div class="space-y-2">
                <a href="${item.file_path}" target="_blank" class="inline-block font-semibold text-sky-400 hover:underline">View Full Image ↗</a>
            </div>`;
    } else if (item.item_type === 'file') {
        const sizeMb = item.file_size ? (item.file_size / (1024 * 1024)).toFixed(2) : 'N/A';
        contentHtml = `
            <div class="bg-slate-900/60 p-3 rounded border border-slate-700/60 flex items-center justify-between">
                <div>
                    <p class="font-medium text-slate-200 [word-break:break-word]">${escapeHtml(item.content)}</p>
                    <span class="text-xs text-slate-500">${sizeMb} MB</span>
                </div>
                <a href="${item.file_path}" target="_blank" class="bg-sky-600 hover:bg-sky-500 text-white text-xs px-3 py-1.5 rounded shrink-0 font-medium">Download</a>
            </div>`;
    } else {
        contentHtml = `<p class="text-slate-300 whitespace-pre-wrap [word-break:break-word]">${escapeHtml(item.content)}</p>`;
    }

    return `
        <div class="bg-slate-800 p-4 rounded border border-slate-700 flex flex-col justify-between">
            <div>
                <div class="flex justify-between items-start mb-2">
                    <span class="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
                        item.item_type === 'image' ? 'bg-purple-900/60 text-purple-300' :
                        item.item_type === 'file' ? 'bg-emerald-900/60 text-emerald-300' :
                        item.item_type === 'link' ? 'bg-indigo-900/60 text-indigo-300' : 'bg-slate-700 text-slate-300'
                    }">
                        ${item.item_type}
                    </span>
                    <span class="text-xs text-slate-500">${new Date(item.created_at).toLocaleDateString()}</span>
                </div>
                ${item.title ? `<h3 class="font-bold text-slate-200 mb-1">${escapeHtml(item.title)}</h3>` : ''}
                ${contentHtml}
            </div>
            <div class="mt-4 pt-2 border-t border-slate-700 flex justify-end">
                <button onclick="deleteItem(${item.id})" class="text-xs text-rose-400 hover:text-rose-300">Delete</button>
            </div>
        </div>
    `;
}).join('');