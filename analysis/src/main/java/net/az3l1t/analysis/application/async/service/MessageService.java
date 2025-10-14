package net.az3l1t.analysis.application.async.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.az3l1t.analysis.application.async.mapper.MessageServiceMapper;
import net.az3l1t.analysis.domain.port.in.MessagePublisherUseCase;
import net.az3l1t.analysis.domain.port.out.AnalysisResultPort;
import net.az3l1t.analysis.domain.port.out.MessagePublisherPort;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class MessageService implements MessagePublisherUseCase {
    private final MessagePublisherPort messagePublisherPort;
    private final AnalysisResultPort analysisResultPort;
    private final MessageServiceMapper messageServiceMapper;

    @Override
    public void sendMessage(String id) {
        messagePublisherPort.publish(
                messageServiceMapper.toSendResultsDto(analysisResultPort.findById(id))
        );
        log.info("Message published with id: {}", id);
    }
}
