package net.az3l1t.analysis.infrastructure.adapter.in.artemis;

import lombok.RequiredArgsConstructor;
import net.az3l1t.analysis.domain.port.in.MessagePublisherUseCase;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/message")
@RequiredArgsConstructor
public class MessageController {
    private final MessagePublisherUseCase messagePublisherUseCase;

    @PostMapping("/{id}")
    @ResponseStatus(HttpStatus.OK)
    public void create(@PathVariable String id) {
        messagePublisherUseCase.sendMessage(id);
    }

    @PostMapping("/notification")
    @ResponseStatus(HttpStatus.OK)
    public void sendNotification(@RequestBody NotificationDto notificationDto) {
        messagePublisherUseCase.sendNotification(notificationDto);
    }
}
