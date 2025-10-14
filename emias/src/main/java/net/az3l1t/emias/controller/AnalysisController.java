package net.az3l1t.emias.controller;

import lombok.RequiredArgsConstructor;
import net.az3l1t.emias.dto.SendResultDto;
import net.az3l1t.emias.service.AnalysisService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/results")
@RequiredArgsConstructor
public class AnalysisController {
    private final AnalysisService analystService;

    @GetMapping("/{id}")
    public SendResultDto getResult(@PathVariable String id) {
        return analystService.getById(id);
    }
}
