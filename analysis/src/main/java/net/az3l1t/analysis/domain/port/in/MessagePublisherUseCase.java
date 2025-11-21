package net.az3l1t.analysis.domain.port.in;

import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto;

public interface MessagePublisherUseCase {
    void sendMessage(String id);
    void sendNotification(NotificationDto notificationDto);
}
