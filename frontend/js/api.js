const API = {
    async getStats() {
        const res = await fetch('/api/stats');
        return res.json();
    },

    async getTickets() {
        const res = await fetch('/api/tickets');
        return res.json();
    },

    async getTicketMessages(ticketId) {
        const res = await fetch(`/api/tickets/${ticketId}/messages`);
        return res.json();
    },

    async getKnowledgeBase() {
        const res = await fetch('/api/knowledge-base');
        return res.json();
    }
};

function statusBadge(status) {
    const colors = {
        open: 'bg-blue-100 text-blue-700',
        escalated: 'bg-orange-100 text-orange-700',
        closed: 'bg-green-100 text-green-700',
        repair_scheduled: 'bg-purple-100 text-purple-700'
    };
    const color = colors[status] || 'bg-gray-100 text-gray-700';
    return `<span class="px-2 py-1 rounded-full text-xs font-semibold ${color}">${status}</span>`;
}

function priorityBadge(priority) {
    const colors = {
        urgent: 'bg-red-100 text-red-700',
        normal: 'bg-yellow-100 text-yellow-700',
        low: 'bg-green-100 text-green-700'
    };
    const color = colors[priority] || 'bg-gray-100 text-gray-700';
    return `<span class="px-2 py-1 rounded-full text-xs font-semibold ${color}">${priority}</span>`;
}

function channelIcon(channel) {
    const icons = {
        email: '📧',
        whatsapp: '💬',
        phone: '📞'
    };
    return icons[channel] || '📨';
}
