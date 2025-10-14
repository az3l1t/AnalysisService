package net.az3l1t.analysis.infrastructure.adapter.in.artemis;

import lombok.RequiredArgsConstructor;
import net.az3l1t.analysis.domain.port.in.MessagePublisherUseCase;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/message")
@RequiredArgsConstructor
public class MessageController {
    private final MessagePublisherUseCase messagePublisherUseCase;

    @PostMapping("/{id}")
    public void create(@PathVariable String id) {
        messagePublisherUseCase.sendMessage(id);
    }
}
