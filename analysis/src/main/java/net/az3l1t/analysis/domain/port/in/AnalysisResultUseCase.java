package net.az3l1t.analysis.domain.port.in;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.springframework.data.domain.Page;

import java.util.Optional;

public interface AnalysisResultUseCase {
    AnalysisResult create(CreateInResultDto createInResultDto);
    AnalysisResult update(UpdateInResultDto updateInResultDto);
    Optional<AnalysisResult> getById(String id);
    Page<AnalysisResult> getAll(int page, int size);
    void delete(String id);
    void confirmAnalysisResult(String id);
    SendResultsDto getConfirmedResults(String id);
}
