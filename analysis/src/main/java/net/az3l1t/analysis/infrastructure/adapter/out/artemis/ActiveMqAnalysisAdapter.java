package net.az3l1t.analysis.infrastructure.adapter.out.artemis;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.az3l1t.analysis.domain.port.out.MessagePublisherPort;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class ActiveMqAnalysisAdapter implements MessagePublisherPort {
    private final JmsTemplate jmsTemplate;
    private final ObjectMapper objectMapper;

    @Value("${spring.analysis.queue-send-name}")
    private String queueName;

    @Value("${spring.analysis.notification-queue-name}")
    private String notificationQueueName;

    @Override
    public void publish(SendResultsDto sendResultsDto) {
        try {
            String json = objectMapper.writeValueAsString(sendResultsDto);
            jmsTemplate.convertAndSend(queueName, json);
            log.info("Message sent to queue: {}", queueName);
        } catch (Exception e) {
            log.error("Error sending message to queue {}: {}", queueName, e.getMessage(), e);
        }
    }

    @Override
    public void publishNotification(NotificationDto notificationDto) {
        try {
            String json = objectMapper.writeValueAsString(notificationDto);
            jmsTemplate.convertAndSend(notificationQueueName, json);
            log.info("Notification sent to queue: {} for analysis result: {}", 
                    notificationQueueName, notificationDto.getAnalysisResultId());
        } catch (Exception e) {
            log.error("Error sending notification to queue {}: {}", 
                    notificationQueueName, e.getMessage(), e);
        }
    }
}
