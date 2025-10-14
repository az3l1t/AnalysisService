package net.az3l1t.analysis.infrastructure.adapter.in.rest;

import lombok.RequiredArgsConstructor;
import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.GetOutResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.UpdateOutResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.mapper.ResultControllerMapper;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;
import net.az3l1t.analysis.domain.port.in.AnalysisResultUseCase;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
@RequestMapping("/api/result")
@RequiredArgsConstructor
public class ResultController {
    private final AnalysisResultUseCase analysisResultUseCase;
    private final ResultControllerMapper resultControllerMapper;

    @PostMapping
    public GetOutResultDto create(@RequestBody CreateInResultDto createInResultDto) {
        return resultControllerMapper.toDtoGet(analysisResultUseCase.create(createInResultDto));
    }

    @PutMapping
    public UpdateOutResultDto update(@RequestBody UpdateInResultDto updateInResultDto) {
        return resultControllerMapper.toDtoUpdate(analysisResultUseCase.update(updateInResultDto));
    }

    @PutMapping("/confirm/{id}")
    public void update(@PathVariable String id) {
        analysisResultUseCase.confirmAnalysisResult(id);
    }

    @GetMapping("/{id}")
    public Optional<AnalysisResult> getById(@PathVariable String id) {
        return analysisResultUseCase.getById(id);
    }

    @GetMapping("/external/{id}")
    public SendResultsDto getExternalResult(@PathVariable String id) {
        return analysisResultUseCase.getConfirmedResults(id);
    }

    @GetMapping
    public Page<AnalysisResult> getAll(@RequestParam(defaultValue = "0") int page,
                                       @RequestParam(defaultValue = "10") int size) {
        return analysisResultUseCase.getAll(page, size);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable String id) {
        analysisResultUseCase.delete(id);
    }
}
