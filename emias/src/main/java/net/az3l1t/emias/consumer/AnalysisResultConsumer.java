package net.az3l1t.emias.consumer;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.jms.Message;
import jakarta.jms.TextMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.az3l1t.emias.dto.SendResultDto;
import net.az3l1t.emias.repository.AnalysisRepository;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Component
@Slf4j
@RequiredArgsConstructor
public class AnalysisResultConsumer {
    private final RedisTemplate<String, String> redisTemplate;
    private final AnalysisRepository analysisRepository;
    private final ObjectMapper objectMapper;

    @JmsListener(destination = "${spring.analysis.queue-send-name}")
    public void receive(Message message) {
        try {
            if (message instanceof TextMessage textMessage) {
                String json = textMessage.getText();
                SendResultDto results = objectMapper.readValue(json, SendResultDto.class);
                log.info("Received message: {}", results);
                analysisRepository.save("analysis:" + results.id(), json);
            } else {
                log.warn("Unsupported message type: {}", message.getClass());
            }
        } catch (Exception e) {
            log.error(e.getMessage(), e);
        }
    }
}
