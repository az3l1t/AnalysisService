package net.az3l1t.analysis.application.rest.client;

import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@FeignClient(name = "emiasClient", url = "${emias.url}")
public interface EmiasClient {
    @GetMapping("/api/results/{id}")
    SendResultsDto getResultById(@PathVariable("id") String id);
}
