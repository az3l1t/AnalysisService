package net.az3l1t.analysis.domain.port.out;

import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;

public interface MessagePublisherPort {
    void publish(SendResultsDto sendResultsDto);
    void publishNotification(NotificationDto notificationDto);
}
