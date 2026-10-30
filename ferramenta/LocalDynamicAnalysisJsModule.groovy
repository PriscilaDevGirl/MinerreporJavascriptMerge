package injectors

import com.google.inject.AbstractModule
import com.google.inject.multibindings.Multibinder
import interfaces.CommitFilter
import interfaces.DataCollector
import interfaces.OutputProcessor
import interfaces.ProjectProcessor
import services.commitFilters.MutuallyModifiedFilesCommitFilter
import services.dataCollectors.StatisticsCollector
import services.dataCollectors.modifiedLinesCollector.ModifiedFilesLinesPerFileCollector

/** Configuration for existing LOCAL clones; official filter and collectors unchanged.
 * The upstream GitHub existence processor rejects local paths, so it is omitted.
 */
class LocalDynamicAnalysisJsModule extends AbstractModule {
    @Override
    protected void configure() {
        def collectors = Multibinder.newSetBinder(binder(), DataCollector.class)
        collectors.addBinding().to(ModifiedFilesLinesPerFileCollector.class)
        collectors.addBinding().to(StatisticsCollector.class)
        bind(CommitFilter.class).to(MutuallyModifiedFilesCommitFilter.class)
        Multibinder.newSetBinder(binder(), ProjectProcessor.class)
        Multibinder.newSetBinder(binder(), OutputProcessor.class)
    }
}
