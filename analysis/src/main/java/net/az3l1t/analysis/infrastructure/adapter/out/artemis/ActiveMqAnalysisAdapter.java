package net.az3l1t.analysis.infrastructure.adapter.out.artemis;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.az3l1t.analysis.domain.port.out.MessagePublisherPort;
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

    @Override
    public void publish(SendResultsDto sendResultsDto) {
        try {
            String json = objectMapper.writeValueAsString(sendResultsDto);
            jmsTemplate.convertAndSend(queueName, json);
        } catch (Exception e) {
            log.error(e.getMessage(), e);
        }
    }
}
