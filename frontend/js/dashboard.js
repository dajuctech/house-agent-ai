async function loadStats() {
    const data = await API.getStats();
    document.getElementById('stat-total').textContent = data.total;
    document.getElementById('stat-open').textContent = data.open;
    document.getElementById('stat-urgent').textContent = data.urgent;
    document.getElementById('stat-escalated').textContent = data.escalated;
    document.getElementById('stat-closed').textContent = data.closed;
}

async function loadTickets() {
    const data = await API.getTickets();
    const tbody = document.getElementById('tickets-table');
    const cards = document.getElementById('tickets-cards');
    const tickets = data.tickets.slice(-10).reverse();

    if (tickets.length === 0) {
        if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-400">No tickets yet</td></tr>';
        if (cards) cards.innerHTML = '<div class="px-4 py-8 text-center text-gray-400 text-sm">No tickets yet</div>';
        return;
    }

    if (tbody) {
        tbody.innerHTML = tickets.map(t => `
            <tr class="hover:bg-gray-50 cursor-pointer" onclick="window.location='/tickets?id=${t.ticket_id}'">
                <td class="px-6 py-4 font-mono text-xs text-gray-500">${t.ticket_id}</td>
                <td class="px-6 py-4 text-gray-800">${t.customer_id}</td>
                <td class="px-6 py-4">${channelIcon(t.channel)} ${t.channel}</td>
                <td class="px-6 py-4">${statusBadge(t.status)}</td>
                <td class="px-6 py-4">${priorityBadge(t.priority)}</td>
                <td class="px-6 py-4 text-gray-600 max-w-xs truncate">${t.summary || '—'}</td>
                <td class="px-6 py-4 text-gray-400 text-xs">${t.created_at}</td>
            </tr>
        `).join('');
    }

    if (cards) {
        cards.innerHTML = tickets.map(t => `
            <div class="px-4 py-4 cursor-pointer hover:bg-gray-50" onclick="window.location='/tickets?id=${t.ticket_id}'">
                <div class="flex items-center justify-between mb-2">
                    <span class="font-mono text-xs text-gray-400">${t.ticket_id}</span>
                    <span>${priorityBadge(t.priority)}</span>
                </div>
                <div class="flex items-center justify-between mb-1">
                    <span class="text-sm font-medium text-gray-800">${t.customer_id}</span>
                    <span>${statusBadge(t.status)}</span>
                </div>
                <p class="text-xs text-gray-500 truncate">${t.summary || '—'}</p>
                <p class="text-xs text-gray-400 mt-1">${channelIcon(t.channel)} ${t.channel} · ${t.created_at}</p>
            </div>
        `).join('');
    }
}

loadStats();
loadTickets();
