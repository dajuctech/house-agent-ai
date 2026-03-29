async function loadTickets() {
    const tbody = document.getElementById('tickets-body');
    const cards = document.getElementById('tickets-cards');
    try {
        const data = await API.getTickets();
        const tickets = data.tickets || [];

        if (tickets.length === 0) {
            if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-10 text-center text-gray-400">No tickets yet.</td></tr>';
            if (cards) cards.innerHTML = '<div class="px-4 py-8 text-center text-gray-400 text-sm">No tickets yet.</div>';
            return;
        }

        // Store tickets by id for quick lookup
        window._ticketMap = {};
        tickets.forEach(t => { window._ticketMap[t.ticket_id] = t; });

        if (tbody) {
            tbody.innerHTML = tickets.map(t => `
                <tr class="hover:bg-gray-50 cursor-pointer" onclick="openTicketById('${t.ticket_id}')">
                    <td class="px-6 py-4 font-mono text-xs text-gray-500">${t.ticket_id || '—'}</td>
                    <td class="px-6 py-4">${t.tenant_contact || '—'}</td>
                    <td class="px-6 py-4">${channelIcon(t.channel)} ${t.channel || '—'}</td>
                    <td class="px-6 py-4">${statusBadge(t.status)}</td>
                    <td class="px-6 py-4">${priorityBadge(t.priority)}</td>
                    <td class="px-6 py-4 max-w-xs truncate">${t.summary || '—'}</td>
                    <td class="px-6 py-4 text-gray-400 text-xs">${t.created_at || '—'}</td>
                </tr>
            `).join('');
        }

        if (cards) {
            cards.innerHTML = tickets.map(t => `
                <div class="px-4 py-4 cursor-pointer hover:bg-gray-50" onclick="openTicketById('${t.ticket_id}')">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-mono text-xs text-gray-400">${t.ticket_id || '—'}</span>
                        <span>${priorityBadge(t.priority)}</span>
                    </div>
                    <div class="flex items-center justify-between mb-1">
                        <span class="text-sm font-medium text-gray-800">${t.tenant_contact || '—'}</span>
                        <span>${statusBadge(t.status)}</span>
                    </div>
                    <p class="text-xs text-gray-500 truncate">${t.summary || '—'}</p>
                    <p class="text-xs text-gray-400 mt-1">${channelIcon(t.channel)} ${t.channel || '—'} · ${t.created_at || '—'}</p>
                </div>
            `).join('');
        }

    } catch (e) {
        if (tbody) tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-10 text-center text-red-400">Failed to load tickets.</td></tr>';
        if (cards) cards.innerHTML = '<div class="px-4 py-8 text-center text-red-400 text-sm">Failed to load tickets.</div>';
    }
}

function openTicketById(ticketId) {
    const ticket = (window._ticketMap || {})[ticketId];
    if (ticket) openTicket(ticketId, ticket);
}

async function openTicket(ticketId, ticket) {

    window._currentTicketId = ticketId;

    document.getElementById('modal-ticket-id').textContent = ticketId;
    document.getElementById('modal-tenant').textContent = ticket.tenant_contact || '—';
    document.getElementById('modal-channel').textContent = ticket.channel || '—';
    document.getElementById('modal-status').innerHTML = statusBadge(ticket.status);
    document.getElementById('modal-priority').innerHTML = priorityBadge(ticket.priority);
    document.getElementById('modal-summary').textContent = ticket.summary || '—';
    document.getElementById('modal-created').textContent = ticket.created_at || '—';
    document.getElementById('modal-messages').innerHTML = '<p class="text-gray-400 text-sm">Loading messages...</p>';
    document.getElementById('modal-status-select').value = ticket.status || 'open';
    document.getElementById('status-update-msg').classList.add('hidden');

    document.getElementById('ticket-modal').classList.remove('hidden');

    try {
        const data = await API.getTicketMessages(ticketId);
        const messages = data.messages || [];
        if (messages.length === 0) {
            document.getElementById('modal-messages').innerHTML = '<p class="text-gray-400 text-sm">No messages yet.</p>';
        } else {
            document.getElementById('modal-messages').innerHTML = messages.map(m => `
                <div class="border rounded-lg p-3 mb-2 ${m.direction === 'outbound' ? 'bg-blue-50 border-blue-100' : 'bg-gray-50'}">
                    <div class="flex justify-between text-xs text-gray-400 mb-1">
                        <span>${m.direction === 'outbound' ? '🤖 Agent' : '👤 Tenant'}</span>
                        <span>${m.timestamp || ''}</span>
                    </div>
                    <p class="text-sm text-gray-700">${m.content || m.body || '—'}</p>
                </div>
            `).join('');
        }
    } catch (e) {
        document.getElementById('modal-messages').innerHTML = '<p class="text-red-400 text-sm">Failed to load messages.</p>';
    }
}

async function updateTicketStatus() {
    const ticketId = window._currentTicketId;
    const status = document.getElementById('modal-status-select').value;
    const msg = document.getElementById('status-update-msg');

    try {
        const res = await fetch(`/api/tickets/${ticketId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        const data = await res.json();
        msg.textContent = data.status === 'updated' ? '✅ Status updated successfully' : '❌ Ticket not found';
        msg.className = `text-xs mt-2 ${data.status === 'updated' ? 'text-green-600' : 'text-red-500'}`;
        msg.classList.remove('hidden');
        if (data.status === 'updated') {
            document.getElementById('modal-status').innerHTML = statusBadge(status);
            await loadTickets();
        }
    } catch (e) {
        msg.textContent = '❌ Failed to update status';
        msg.className = 'text-xs mt-2 text-red-500';
        msg.classList.remove('hidden');
    }
}

function closeModal() {
    document.getElementById('ticket-modal').classList.add('hidden');
}

async function loadTicketsAndAutoOpen() {
    await loadTickets();
    const params = new URLSearchParams(window.location.search);

    // Apply filter if present
    const filter = params.get('filter');
    if (filter && filter !== 'all') {
        const heading = document.getElementById('tickets-heading');
        const clearBtn = document.getElementById('clear-filter');
        const labels = { open: 'Open', urgent: 'Urgent', escalated: 'Escalated', closed: 'Closed' };
        if (heading) heading.textContent = (labels[filter] || filter) + ' Tickets';
        if (clearBtn) clearBtn.classList.remove('hidden');

        // Filter table rows
        const tbody = document.getElementById('tickets-body');
        if (tbody) {
            Array.from(tbody.querySelectorAll('tr')).forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        }
        // Filter mobile cards
        const cards = document.getElementById('tickets-cards');
        if (cards) {
            Array.from(cards.querySelectorAll('[onclick]')).forEach(card => {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(filter) ? '' : 'none';
            });
        }
    }

    // Auto-open ticket by id
    const id = params.get('id');
    if (id && window._ticketMap && window._ticketMap[id]) {
        openTicket(id, window._ticketMap[id]);
    }
}

loadTicketsAndAutoOpen();
